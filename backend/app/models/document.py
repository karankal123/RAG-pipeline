from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Element(BaseModel):
    type: str
    text: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    content_type: Optional[str] = None
    table_id: Optional[str] = None
    image_id: Optional[str] = None
    bbox: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentResource(BaseModel):
    document_id: str
    application_id: str
    filename: str
    version: str = "v1"
    content_type: str = "application/pdf"
    pages: int = 0
    elements: List[Element] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    application_id: str
    page: Optional[int] = None
    section: Optional[str] = None
    content_type: str = "text"
    parent_id: Optional[str] = None
    text: str
    table_id: Optional[str] = None
    image_id: Optional[str] = None
    version: str = "v1"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str
    score: float
    page: Optional[int]
    section: Optional[str]
    content_type: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
