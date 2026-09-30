from __future__ import annotations

from typing import List

from app.models.document import Chunk, DocumentResource


class ChunkingService:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: DocumentResource) -> List[Chunk]:
        chunks: List[Chunk] = []
        text_blocks = []
        for element in document.elements:
            if element.text:
                text_blocks.append(element.text)
        combined = "\n".join(text_blocks)

        if not combined.strip():
            combined = "Loan document text unavailable."

        start = 0
        index = 0
        while start < len(combined):
            end = min(len(combined), start + self.chunk_size)
            chunk_text = combined[start:end]
            chunk = Chunk(
                chunk_id=f"{document.document_id}-chunk-{index}",
                document_id=document.document_id,
                application_id=document.application_id,
                page=1,
                section="Loan Details",
                content_type="text",
                text=chunk_text,
                version=document.metadata.get("version", "v1"),
                metadata={"source": document.filename, "chunk_index": index},
            )
            chunks.append(chunk)
            index += 1
            start = end - self.chunk_overlap if end < len(combined) else end

        return chunks
