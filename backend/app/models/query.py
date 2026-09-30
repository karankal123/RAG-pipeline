from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


QueryType = Literal[
    "text",
    "exact_lookup",
    "table",
    "image",
    "metadata",
    "cross_document",
    "multi_hop",
    "calculation",
    "comparison",
]


class QueryRequest(BaseModel):
    question: str
    application_id: Optional[str] = None
    version: Optional[str] = None
    top_k: int = 5
    retrieval_type: str = "hybrid"


class QueryClassification(BaseModel):
    query_type: QueryType
    rewritten_query: str
    keywords: List[str] = Field(default_factory=list)
    metadata_filters: Dict[str, Any] = Field(default_factory=dict)


class RAGPipelineResponse(BaseModel):
    answer: str
    citations: List[str] = Field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    query_type: str
    rewritten_query: str
    model_used: str
