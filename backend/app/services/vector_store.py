from __future__ import annotations

from typing import Dict, List, Tuple

import faiss
import numpy as np

from app.models.document import Chunk


class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: Dict[str, Dict] = {}
        self._index_to_chunk: List[str] = []

    def upsert(self, chunk: Chunk, embedding: np.ndarray):
        vector = np.asarray(embedding, dtype="float32").reshape(1, -1)
        self.index.add(vector)
        index = len(self._index_to_chunk)
        self._index_to_chunk.append(chunk.chunk_id)
        self.metadata[chunk.chunk_id] = {
            "document_id": chunk.document_id,
            "application_id": chunk.application_id,
            "chunk_id": chunk.chunk_id,
            "page": chunk.page,
            "section": chunk.section,
            "content_type": chunk.content_type,
            "version": chunk.version,
            "text": chunk.text,
            "_index": index,
        }

    def search(self, query_vector: np.ndarray, top_k: int = 5, filters: Dict | None = None) -> List[Tuple[str, float]]:
        if self.index.ntotal == 0:
            return []

        distances, indices = self.index.search(np.asarray(query_vector, dtype="float32").reshape(1, -1), min(top_k, self.index.ntotal))
        results: List[Tuple[str, float]] = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            chunk_id = self._index_to_chunk[int(idx)] if 0 <= int(idx) < len(self._index_to_chunk) else None
            if not chunk_id:
                continue
            if filters:
                meta = self.metadata.get(chunk_id, {})
                if not all(meta.get(key) == value for key, value in filters.items()):
                    continue
            results.append((chunk_id, float(distance)))
        return results

    def reset(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata.clear()
        self._index_to_chunk.clear()
