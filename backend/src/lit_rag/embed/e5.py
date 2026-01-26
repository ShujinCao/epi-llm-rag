from __future__ import annotations

from dataclasses import dataclass
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

@dataclass
class E5Embedder:
    model_name: str
    _model: SentenceTransformer | None = None

    def load(self) -> None:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

    def embed_passages(self, passages: List[str], batch_size: int = 32) -> np.ndarray:
        self.load()
        assert self._model is not None
        texts = [f"passage: {p}" for p in passages]
        v = self._model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
        return np.asarray(v, dtype="float32")

    def embed_query(self, query: str) -> np.ndarray:
        self.load()
        assert self._model is not None
        v = self._model.encode([f"query: {query}"], normalize_embeddings=True)
        return np.asarray(v[0], dtype="float32")
