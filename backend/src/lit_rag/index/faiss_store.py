from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np
import faiss

from lit_rag.index.schema import Chunk, SearchHit

@dataclass
class FaissIndexBundle:
    index: Any
    id_map: List[str]          # index position -> chunk_id
    meta: Dict[str, Chunk]     # chunk_id -> Chunk

def _normalize(v: np.ndarray) -> np.ndarray:
    # L2 normalize along last dim
    norms = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / norms

def build_index(chunks: List[Chunk], vectors: np.ndarray) -> FaissIndexBundle:
    # vectors expected shape: (N, D)
    vectors = vectors.astype("float32")
    vectors = _normalize(vectors)

    d = vectors.shape[1]
    # Inner Product on normalized vectors == cosine similarity
    index = faiss.IndexFlatIP(d)
    index.add(vectors)

    id_map = [c.chunk_id for c in chunks]
    meta = {c.chunk_id: c for c in chunks}
    return FaissIndexBundle(index=index, id_map=id_map, meta=meta)

def save_bundle(bundle: FaissIndexBundle, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(bundle.index, str(out_dir / "index.faiss"))

    (out_dir / "id_map.json").write_text(json.dumps(bundle.id_map, indent=2), encoding="utf-8")
    # meta as JSONL for easy streaming
    with (out_dir / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for cid in bundle.id_map:
            f.write(bundle.meta[cid].model_dump_json())
            f.write("\n")

def load_bundle(index_dir: Path) -> FaissIndexBundle:
    index = faiss.read_index(str(index_dir / "index.faiss"))
    id_map = json.loads((index_dir / "id_map.json").read_text(encoding="utf-8"))

    meta: Dict[str, Chunk] = {}
    with (index_dir / "chunks.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c = Chunk.model_validate_json(line)
                meta[c.chunk_id] = c

    return FaissIndexBundle(index=index, id_map=id_map, meta=meta)

def search(bundle: FaissIndexBundle, query_vec: np.ndarray, k: int = 8) -> List[SearchHit]:
    q = query_vec.astype("float32")
    q = q.reshape(1, -1)
    q = _normalize(q)

    scores, idxs = bundle.index.search(q, k)
    out: List[SearchHit] = []
    for score, ix in zip(scores[0].tolist(), idxs[0].tolist()):
        if ix < 0:
            continue
        cid = bundle.id_map[ix]
        c = bundle.meta[cid]
        out.append(SearchHit(
            chunk_id=cid,
            paper_id=c.paper_id,
            score=float(score),
            section=c.section,
            text=c.text,
            title=c.title,
            year=c.year,
            source=c.source,
        ))
    return out
