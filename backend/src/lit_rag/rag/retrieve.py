from __future__ import annotations

from pathlib import Path
from typing import List

from lit_rag.config import settings
from lit_rag.embed.e5 import E5Embedder
from lit_rag.index.faiss_store import load_bundle, search as faiss_search
from lit_rag.index.schema import SearchHit

class Retriever:
    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.bundle = load_bundle(index_dir)
        self.embedder = E5Embedder(settings.e5_model)

    def search(self, query: str, k: int = 8) -> List[SearchHit]:
        qv = self.embedder.embed_query(query)
        return faiss_search(self.bundle, qv, k=k)
