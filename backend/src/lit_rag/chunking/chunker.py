from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import hashlib

from lit_rag.chunking.section_split import split_into_sections
from lit_rag.index.schema import Chunk

@dataclass
class Chunker:
    chunk_chars: int = 1400
    overlap_chars: int = 250

    def _make_id(self, paper_id: str, section: str, ordinal: int, text: str) -> str:
        h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        return f"{paper_id}:{section}:{ordinal}:{h}"

    def chunk_text(self, *, paper_id: str, source: str, title: Optional[str], year: Optional[int], text: str) -> List[Chunk]:
        sections = split_into_sections(text)
        chunks: List[Chunk] = []
        for section_name, section_text in sections:
            s = section_text.strip()
            if not s:
                continue
            start = 0
            ordinal = 0
            while start < len(s):
                end = min(len(s), start + self.chunk_chars)
                piece = s[start:end]
                cid = self._make_id(paper_id, section_name.replace(" ", "_"), ordinal, piece)
                chunks.append(Chunk(
                    chunk_id=cid,
                    paper_id=paper_id,
                    source=source,
                    title=title,
                    year=year,
                    section=section_name,
                    text=piece
                ))
                ordinal += 1
                if end == len(s):
                    break
                start = max(0, end - self.overlap_chars)
        return chunks
