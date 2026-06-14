import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "./libs/rag/chunks.jsonl"
FAISS_INDEX_PATH = "./libs/rag/faiss_index.bin"
METADATA_PATH = "./libs/rag/faiss_metadata.json"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks(file_path):
    chunks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def create_and_save_faiss_index(chunks, model, index_path, metadata_path):
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    embeddings = model.encode([chunk["content"] for chunk in chunks], show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)

    # Store content alongside metadata so semantic_search can return it
    records = [
        {**chunk["metadata"], "content": chunk["content"]}
        for chunk in chunks
    ]
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"FAISS index created with {index.ntotal} vectors and saved to {index_path}")
    print(f"Metadata saved to {metadata_path}")
    return index


def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"FAISS index loaded from {index_path} with {index.ntotal} vectors.")
    return index, metadata


def semantic_search(query, model, faiss_index, metadata, k=5):
    query_embedding = model.encode([query]).astype("float32")
    distances, indices = faiss_index.search(query_embedding, k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        record = metadata[idx]
        results.append({
            "score": float(distances[0][i]),
            "content": record.get("content", ""),
            "metadata": {k: v for k, v in record.items() if k != "content"},
        })
    return results


def main():
    chunks = load_chunks(CHUNKS_FILE)
    if not chunks:
        print("No chunks found. Please run chunk_documents.py first.")
        return

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    faiss_index = create_and_save_faiss_index(chunks, model, FAISS_INDEX_PATH, METADATA_PATH)

    print("\n--- Sample Semantic Search ---")
    sample_query = "How should I write content for a blog post?"
    print(f"Query: '{sample_query}'")

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    search_results = semantic_search(sample_query, model, faiss_index, metadata)
    for i, result in enumerate(search_results):
        print(f"\nResult {i + 1} (Score: {result['score']:.4f}):")
        print(f"  Source: {result['metadata'].get('source_path')}")
        print(f"  Type:   {result['metadata'].get('source_type')}")
        print(f"  Content preview: {result['content'][:200]}")


if __name__ == "__main__":
    main()
