import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "./libs/rag/chunks.jsonl"
FAISS_INDEX_PATH = "./libs/rag/faiss_index.bin"
METADATA_PATH = "./libs/rag/faiss_metadata.json"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level cache so FastAPI loads these once at startup
_model: SentenceTransformer | None = None
_faiss_index: faiss.Index | None = None
_metadata: list | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def get_index(
    index_path: str = FAISS_INDEX_PATH,
    metadata_path: str = METADATA_PATH,
) -> tuple[faiss.Index, list]:
    global _faiss_index, _metadata
    if _faiss_index is None or _metadata is None:
        _faiss_index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
        print(f"FAISS index loaded with {_faiss_index.ntotal} vectors.")
    return _faiss_index, _metadata


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Main entry point for FastAPI — returns top-k chunks for a query."""
    model = get_model()
    faiss_index, metadata = get_index()

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
            "metadata": {key: val for key, val in record.items() if key != "content"},
        })
    return results


# --- Build-time helpers (run directly to generate the index) ---

def load_chunks(file_path: str = CHUNKS_FILE) -> list[dict]:
    chunks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def build_index(
    chunks_file: str = CHUNKS_FILE,
    index_path: str = FAISS_INDEX_PATH,
    metadata_path: str = METADATA_PATH,
) -> None:
    chunks = load_chunks(chunks_file)
    if not chunks:
        raise RuntimeError(f"No chunks found in {chunks_file}. Run chunk_documents.py first.")

    model = get_model()
    embeddings = model.encode([c["content"] for c in chunks], show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)

    records = [{**c["metadata"], "content": c["content"]} for c in chunks]
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"FAISS index created with {index.ntotal} vectors → {index_path}")
    print(f"Metadata saved → {metadata_path}")


def main():
    build_index()

    print("\n--- Sample Semantic Search ---")
    query = "How should I write content for a blog post?"
    print(f"Query: '{query}'")
    for i, result in enumerate(retrieve(query)):
        print(f"\nResult {i + 1} (Score: {result['score']:.4f}):")
        print(f"  Source:  {result['metadata'].get('source_path')}")
        print(f"  Type:    {result['metadata'].get('source_type')}")
        print(f"  Preview: {result['content'][:200]}")


if __name__ == "__main__":
    main()
