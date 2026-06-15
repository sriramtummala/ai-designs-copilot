# State of the RAG System: Week 3 Review
 
## 1. Introduction
 
 The RAG system is designed to ground the Large Language Model (LLM) in a curated and approved knowledge base, ensuring that generated content is accurate, compliant, and on-brand.
 
## 2. RAG System Components
 
The RAG system comprises several interconnected components:
 
### 2.1 Knowledge Base
 
*   **Location:** `knowledge/` directory within the monorepo.
*   **Content:** Markdown files containing brand guidelines, design system rules, CMS page rules, and other approved documentation.
*   **Purpose:** Serves as the single source of truth for all information provided to the LLM.
 
### 2.2 Chunking and Metadata Design
 
*   **Script:** `libs/rag/create_embeddings.py` (initially, now integrated).
*   **Process:** Raw Markdown documents are split into smaller, semantically meaningful chunks. Each chunk is enriched with metadata (e.g., `source_type`, `brand`, `approved`, `version`).
*   **Output:** `libs/rag/chunks.jsonl` (JSONL format).
 
### 2.3 Vector Embeddings and Local Vector Store
 
*   **Model:** `sentence-transformers/all-MiniLM-L6-v2`.
*   **Process:** Text chunks are converted into high-dimensional numerical vectors (embeddings) that capture their semantic meaning.
*   **Vector Store:** FAISS (Facebook AI Similarity Search) is used as a local, in-memory vector database.
*   **Output:** `libs/rag/faiss_index.bin` and `libs/rag/faiss_metadata.json`.
 
### 2.4 LLM Integration and Content Generation
 
*   **Client:** OpenAI Python client.
*   **Model:** Configurable via `OPENAI_MODEL` environment variable (e.g., `gpt-4o-mini`).
*   **Endpoint:** `/generate` in `apps/api/main.py`.
*   **Process:** Orchestrates the retrieval of relevant context from the vector store based on user request, constructs a detailed prompt (using `libs/llm/prompts.py`), and sends it to the LLM for content generation.
 
## 3. Data Flow in the RAG Pipeline
 
1.  **User Request:** A `GenerationRequest` is sent to the `/generate` endpoint of the FastAPI backend.
2.  **Context Retrieval:** The `/generate` endpoint formulates a query and calls the `/rag/retrieve` endpoint.
3.  **Semantic Search:** The `/rag/retrieve` endpoint uses the embedding model to convert the query into a vector, performs a semantic search against the FAISS index, and retrieves the top `k` most relevant chunks, applying metadata filters.
4.  **Prompt Construction:** The retrieved chunks are combined with the original user request details and injected into a system prompt and user prompt template.
5.  **LLM Call:** The constructed prompts are sent to the OpenAI LLM via the `openai_client`.
6.  **Content Generation:** The LLM generates structured content based on the prompt and context.
7.  **Response:** The generated content, along with the retrieved context and LLM parameters, is returned to the user.
 
## 4. Challenges and Solutions
 
*   **Challenge:** Ensuring consistent and accurate content generation across different brands and channels.
    *   **Solution:** Strict adherence to a structured knowledge base, metadata filtering during retrieval, and detailed prompt engineering to enforce guidelines.
*   **Challenge:** Managing LLM output variability.
    *   **Solution:** Implemented configurable LLM parameters (`temperature`, `top_p`, `frequency_penalty`, `presence_penalty`) in the `/generate` endpoint to allow fine-tuning of creativity vs. adherence.
*   **Challenge:** Evaluating the quality and relevance of generated content.
    *   **Solution:** Developed a `/feedback` endpoint to capture human evaluations (user ratings, comments) for continuous improvement.
 
## 5. Evaluation and Feedback
 
The `/feedback` endpoint (`/data/feedback.jsonl`) provides a mechanism for human-in-the-loop evaluation. This data will be crucial for:
 
*   Identifying areas where the RAG system (retrieval or generation) needs improvement.
*   Quantifying the impact of prompt engineering changes or LLM parameter adjustments.
*   Ensuring alignment with brand and compliance standards.
 
 
