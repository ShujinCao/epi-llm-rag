from __future__ import annotations

from typing import Dict, Any, List
from lit_rag.index.schema import SearchHit

def simple_answer(hits: List[SearchHit]) -> Dict[str, Any]:
    # v1: return passages; extraction endpoint is separate
    return {
        "hits": [h.model_dump() for h in hits]
    }
