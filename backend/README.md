# Loan Intelligence Multimodal RAG

This project is a lightweight but production-oriented RAG foundation for enterprise loan-document analysis. It follows the brief in `prompt.txt` by providing:

- a FastAPI backend
- a modular document ingestion pipeline
- chunking and vector indexing
- semantic retrieval with metadata filters
- query classification
- evidence-backed answer generation
- a simple frontend dashboard

## Quick start

1. Open a terminal in `backend`.
2. Install dependencies:
   `python -m pip install -r requirements.txt`
3. Run the server:
   `python main.py`
4. Visit `http://localhost:8000/docs` for Swagger.

## Major architecture components

- `app/services/document_parser.py` — parser abstraction for PDFs and text docs
- `app/services/chunking_service.py` — chunk creation and metadata retention
- `app/services/embedding_service.py` — dense embeddings with a deterministic fallback
- `app/services/vector_store.py` — FAISS-based retrieval and metadata filtering
- `app/services/query_router.py` — classification and rewrite logic
- `app/services/rag_pipeline.py` — orchestration from upload to answer generation

## Notes

This is a functioning MVP, not a full Azure-native enterprise system. It is intentionally designed so the architecture can be expanded to include OCR, Azure Document Intelligence, multiparser extraction, hybrid retrieval, reranking, and evaluation workflows without rewriting the core interfaces.
