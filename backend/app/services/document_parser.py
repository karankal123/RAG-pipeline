from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.models.document import DocumentResource, Element


@dataclass
class ParsedDocument:
    document: DocumentResource
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentParser:
    """Abstract-like parser interface that normalizes extracted document content."""

    def parse(self, filename: str, content: bytes, application_id: str = "APP-001") -> ParsedDocument:
        text = self._extract_text(content)
        elements = [
            Element(type="heading", text="Loan Application", page=1, section="Summary", content_type="text"),
            Element(type="paragraph", text=text[:2000], page=1, section="Main", content_type="text"),
        ]
        document = DocumentResource(
            document_id=f"DOC-{hash(filename) & 0xFFFFFFFF:08x}",
            application_id=application_id,
            filename=filename,
            pages=1,
            elements=elements,
            metadata={"source": "uploaded_file", "parsed_by": "document_parser"},
        )
        return ParsedDocument(document=document, raw_text=text, metadata={"pages": 1})

    def _extract_text(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
            import io

            if content[:5].lower() == b"%pdf-":
                reader = PdfReader(io.BytesIO(content))
                pages = []
                for page in reader.pages:
                    pages.append(page.extract_text() or "")
                return "\n".join(pages)
        except Exception:
            pass

        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return "Uploaded document text could not be extracted automatically."
