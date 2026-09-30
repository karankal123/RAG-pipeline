from __future__ import annotations

import re
from typing import Any, Dict, List

from app.models.query import QueryClassification, QueryType


class QueryRouter:
    def classify(self, question: str, application_id: str | None = None) -> QueryClassification:
        normalized = question.strip()
        lowered = normalized.lower()

        query_type: QueryType = "text"
        if any(term in lowered for term in ["income", "expense", "liability", "salary", "monthly", "variance"]):
            query_type = "calculation"
        elif any(term in lowered for term in ["application id", "document id", "version", "page", "status"]):
            query_type = "metadata"
        elif any(term in lowered for term in ["compare", "difference", "inconsistent", "conflict", "discrepancy"]):
            query_type = "comparison"
        elif any(term in lowered for term in ["table", "amount", "monthly", "living expense"]):
            query_type = "table"
        elif any(term in lowered for term in ["signature", "checkbox", "acknowledged", "credit guide"]):
            query_type = "metadata"

        keywords = re.findall(r"[A-Za-z][A-Za-z0-9-]+", normalized)
        rewritten = normalized
        if application_id:
            rewritten = f"{normalized} for application {application_id}"

        metadata_filters: Dict[str, Any] = {}
        if application_id:
            metadata_filters["application_id"] = application_id

        return QueryClassification(
            query_type=query_type,
            rewritten_query=rewritten,
            keywords=[k.lower() for k in keywords][:10],
            metadata_filters=metadata_filters,
        )
