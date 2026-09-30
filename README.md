# Loan Intelligence Multimodal RAG

A production-oriented MVP for exploring retrieval-augmented generation over loan application documents. The project is based on the requirements in [prompt.txt](prompt.txt) and provides a modular foundation for document parsing, chunking, embeddings, vector retrieval, query routing, and evidence-backed answers.

## Current MVP

The current implementation includes:

- FastAPI backend with OpenAPI documentation
- React + TypeScript + Vite frontend
- PDF and text document ingestion
- Normalized document and element models
- Configurable fixed-size chunking with overlap
- Dense embeddings using Sentence Transformers when available
- Deterministic local embedding fallback for development
- FAISS vector search
- Application ID and version metadata filtering
- Basic query classification and query rewriting
- Retrieved chunk metadata and source/page citations
- Health, upload, document listing, and query APIs

The system is intentionally modular so Azure AI Document Intelligence, hybrid retrieval, reranking, document versioning, and evaluation can be added without replacing the core pipeline interfaces.

## Architecture

```text
Loan document
    |
    v
DocumentParser
    |
    v
Normalized DocumentResource + Elements
    |
    v
ChunkingService
    |
    v
Chunks with provenance metadata
    |
    v
EmbeddingService
    |
    v
FAISS VectorStore
    |
    v
QueryRouter -> retrieval -> grounded response with citations
```

### Backend modules

| Module | Responsibility |
| --- | --- |
| `backend/app/services/document_parser.py` | Extracts text and creates normalized document elements |
| `backend/app/services/chunking_service.py` | Creates chunks while retaining page, section, and document metadata |
| `backend/app/services/embedding_service.py` | Generates dense embeddings or a deterministic local fallback |
| `backend/app/services/vector_store.py` | Stores vectors and performs similarity search with metadata filters |
| `backend/app/services/query_router.py` | Classifies questions and creates retrieval-friendly rewrites |
| `backend/app/services/rag_pipeline.py` | Coordinates indexing, retrieval, context assembly, and response creation |
| `backend/app/api/routes.py` | Exposes the HTTP API |

## Project structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- models/
|   |   |-- services/
|   |   |-- config.py
|   |-- main.py
|   |-- requirements.txt
|   |-- .env.example
|   `-- README.md
|-- frontend/
|   |-- src/
|   |-- package.json
|   `-- vite.config.ts
|-- prompt.txt
`-- README.md
```

## Prerequisites

- Python 3.13 or compatible Python 3.x runtime
- Node.js 18 or newer
- npm

## Backend setup

From the repository root:

```powershell
Set-Location .\backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

The backend starts at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

The first startup may download the configured Sentence Transformers model. If that model cannot be loaded, the application uses a deterministic local fallback embedding so the API remains runnable for development.

## Frontend setup

Open a second terminal from the repository root:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Open http://localhost:5173.

The frontend expects the backend at `http://localhost:8000`. Start the backend before asking a question in the Retrieval Playground.

To create a production frontend build:

```powershell
npm run build
```

## API reference

### Health check

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok",
  "service": "loan-intelligence-rag"
}
```

### Upload and index a document

```http
POST /api/documents/upload
Content-Type: multipart/form-data
```

Supported file extensions are `.pdf`, `.png`, `.jpg`, `.jpeg`, and `.txt`.

PowerShell example:

```powershell
curl.exe -X POST http://localhost:8000/api/documents/upload `
  -F "file=@C:\path\to\loan-package.pdf"
```

### List indexed documents

```http
GET /api/documents
```

### Ask a question

```http
POST /api/query
Content-Type: application/json
```

Request example:

```json
{
  "question": "What is the applicant's monthly income?",
  "application_id": "APP-001",
  "top_k": 5,
  "retrieval_type": "hybrid"
}
```

Response fields include:

- `answer`: evidence-backed response text
- `citations`: document and page references
- `retrieved_chunks`: retrieved chunk content, scores, and metadata
- `query_type`: classified query category
- `rewritten_query`: normalized retrieval query
- `model_used`: configured embedding model name

## Configuration

Copy `backend/.env.example` to `backend/.env` and change values as needed:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DEFAULT_CHUNK_SIZE=500
DEFAULT_CHUNK_OVERLAP=80
DEFAULT_TOP_K=5
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
```

Secrets should be supplied through environment variables or a local `.env` file. Do not commit `.env` files.

## Validation

Backend syntax check:

```powershell
Set-Location .\backend
python -m compileall app main.py
```

Frontend build check:

```powershell
Set-Location .\frontend
npm run build
```

## Roadmap toward the full enterprise design

The original requirements describe a broader experimentation platform. The next implementation stages are:

1. Add Azure AI Document Intelligence for OCR, layout, tables, forms, signatures, and bounding boxes.
2. Add a parser adapter interface for PyMuPDF, Azure Document Intelligence, and alternative parsers.
3. Add BM25 or Azure AI Search hybrid retrieval with Reciprocal Rank Fusion.
4. Add parent-child and hierarchical retrieval.
5. Add configurable cross-encoder or Azure semantic reranking.
6. Add document hashing, version retirement, and incremental indexing.
7. Add table-aware, image-aware, and multimodal chunk representations.
8. Add Azure OpenAI grounded generation with structured citations and abstention.
9. Add a labeled evaluation dataset and metrics including Recall@K, MRR, NDCG, groundedness, correctness, citation accuracy, latency, and cost.
10. Add retrieval tracing and an evaluation dashboard for comparing single-vector and multi-vector experiments.

## Important limitations of this MVP

- OCR and visual document understanding are not yet connected to Azure AI Document Intelligence.
- Retrieval currently uses FAISS dense search; the `retrieval_type` request field is reserved for future hybrid strategies.
- The current answer layer is a deterministic evidence formatter rather than an LLM generation service.
- Index state is held in process memory and is lost when the backend restarts.
- The frontend currently provides a question playground; full document, chunk, embedding, and evaluation explorers are roadmap items.
- Authentication, authorization, durable storage, background processing, and production observability still need to be added before deployment.

## License

No license has been selected for this repository yet.
