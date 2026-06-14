import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from langchain_text_splitters import MarkdownTextSplitter

# Configuration
KNOWLEDGE_BASE_PATH = "./knowledge"
OUTPUT_FILE = "./libs/rag/chunks.jsonl"

def get_metadata_from_path(filepath):
    """Infers metadata from the file path."""
    parts = Path(filepath).parts
    metadata = {
        "source_path": filepath,
        "last_updated": datetime.now().isoformat(),
        "approved": True,
        "version": "1.0",
    }

    if "knowledge" in parts:
        knowledge_idx = parts.index("knowledge")
        if knowledge_idx + 1 < len(parts):
            category = parts[knowledge_idx + 1]
            metadata["source_type"] = category.replace("-", "_")

            if category == "brand-guidelines":
                metadata["brand"] = "brand_b"
            elif category == "component-registry":
                metadata["component"] = Path(filepath).stem.replace("-component", "").replace("-", "_")
            elif category == "design-tokens":
                metadata["token_type"] = Path(filepath).stem.replace("-", "_")
            elif category == "cms-page-rules":
                metadata["channel"] = "web"
                metadata["page_type"] = Path(filepath).stem.replace("-rules", "").replace("-", "_")

    return metadata
 
def chunk_markdown_file(filepath):
    """Reads a markdown file, chunks it, and adds metadata."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
 
    # Initialize MarkdownTextSplitter
    # This splitter attempts to split along Markdown headings, code blocks, etc.
    markdown_splitter = MarkdownTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
 
    chunks = markdown_splitter.create_documents([content])
    
    base_metadata = get_metadata_from_path(filepath)
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = base_metadata.copy()
        chunk_metadata["chunk_id"] = f"{os.path.basename(filepath)}_{i}"
        chunk_metadata["content_hash"] = hashlib.md5(chunk.page_content.encode()).hexdigest()
        processed_chunks.append({"content": chunk.page_content, "metadata": chunk_metadata})
    
    return processed_chunks
 
def main():
    all_chunks = []
    for root, _, files in os.walk(KNOWLEDGE_BASE_PATH):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                print(f"Processing {filepath}...")
                chunks = chunk_markdown_file(filepath)
                all_chunks.extend(chunks)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
    
    print(f"Successfully generated {len(all_chunks)} chunks to {OUTPUT_FILE}")
 
if __name__ == "__main__":
    main()

