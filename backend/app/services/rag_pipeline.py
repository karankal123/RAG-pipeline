from __future__ import annotations

from typing import Any, Dict, List

from app.config import get_settings
from app.models.document import Chunk, DocumentResource, RetrievalResult
from app.models.query import QueryRequest, RAGPipelineResponse
from app.services.chunking_service import ChunkingService
from app.services.document_parser import DocumentParser
from app.services.embedding_service import EmbeddingService
from app.services.query_router import QueryRouter
from app.services.vector_store import VectorStore


class LoanRAGPipeline:
    def __init__(self):
        settings = get_settings()
        self.chunking_service = ChunkingService(settings.default_chunk_size, settings.default_chunk_overlap)
        self.embedding_service = EmbeddingService(settings.embedding_model)
        self.vector_store = VectorStore(dimension=384)
        self.parser = DocumentParser()
        self.query_router = QueryRouter()
        self.documents: Dict[str, DocumentResource] = {}
        self.chunks: Dict[str, Chunk] = {}

    def index_document_file(self, filename: str, content: bytes, application_id: str = "APP-001") -> DocumentResource:
        parsed = self.parser.parse(filename, content, application_id=application_id)
        document = parsed.document
        self.documents[document.document_id] = document

        chunks = self.chunking_service.chunk_document(document)
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk
            embedding = self.embedding_service.embed_chunk(chunk)
            self.vector_store.upsert(chunk, embedding)

        return document

    def list_documents(self) -> List[DocumentResource]:
        return list(self.documents.values())

    def answer_question(self, request: QueryRequest) -> RAGPipelineResponse:
        classification = self.query_router.classify(request.question, request.application_id)
        query_vector = self.embedding_service.embed_texts([classification.rewritten_query])[0]

        filters = {}
        if request.application_id:
            filters["application_id"] = request.application_id
        if request.version:
            filters["version"] = request.version

        search_results = self.vector_store.search(query_vector, top_k=request.top_k, filters=filters)
        retrieved = []
        for chunk_id, distance in search_results:
            chunk = self.chunks.get(chunk_id)
            if not chunk:
                continue
            retrieved.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    score=float(distance),
                    page=chunk.page,
                    section=chunk.section,
                    content_type=chunk.content_type,
                    text=chunk.text,
                    metadata={"version": chunk.version, "source": self.documents.get(chunk.document_id).filename if chunk.document_id in self.documents else ""},
                )
            )

        if not retrieved:
            answer = "No sufficient evidence was found in the indexed documents for this question."
            citations = []
        else:
            top_text = "\n\n".join(item.text.strip() for item in retrieved[:3])
            answer = (
                f"Based on the available evidence, the most relevant information is: {top_text[:800]}\n\n"
                "The system should treat this as evidence-backed context, not as a claim beyond the retrieved material."
            )
            citations = [
                f"{self.documents.get(item.document_id).filename if item.document_id in self.documents else 'unknown'} — page {item.page or 1}"
                for item in retrieved[:3]
            ]

        return RAGPipelineResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=[r.model_dump() for r in retrieved],
            query_type=classification.query_type,
            rewritten_query=classification.rewritten_query,
            model_used=self.embedding_service.model_name,
        )
