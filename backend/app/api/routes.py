from __future__ import annotations

from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.models.document import DocumentResource
from app.models.query import QueryRequest, RAGPipelineResponse
from app.services.rag_pipeline import LoanRAGPipeline

router = APIRouter(prefix="/api", tags=["rag"])

pipeline = LoanRAGPipeline()


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "service": "loan-intelligence-rag"}


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> DocumentResource:
    if not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".txt")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    content = await file.read()
    document = pipeline.index_document_file(file.filename, content)
    return document


@router.post("/query", response_model=RAGPipelineResponse)
async def answer_question(request: QueryRequest) -> RAGPipelineResponse:
    return pipeline.answer_question(request)


@router.get("/documents")
def list_documents() -> List[DocumentResource]:
    return pipeline.list_documents()
