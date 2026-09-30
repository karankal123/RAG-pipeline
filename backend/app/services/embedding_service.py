from __future__ import annotations

import hashlib
from typing import List

import numpy as np

from app.models.document import Chunk


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
        except Exception:
            self.model = None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return np.asarray(embeddings, dtype="float32")

        return np.asarray([self._fallback_vector(text) for text in texts], dtype="float32")

    def embed_chunk(self, chunk: Chunk) -> np.ndarray:
        return self.embed_texts([chunk.text])[0]

    def _fallback_vector(self, text: str) -> np.ndarray:
        dimension = 384
        vector = np.zeros(dimension, dtype="float32")
        for i in range(dimension):
            digest = hashlib.sha256(f"{text}:{i}".encode("utf-8")).digest()
            value = int.from_bytes(digest[:4], byteorder="big") / float(2**32)
            vector[i] = (value - 0.5) * 2.0
        return vector
