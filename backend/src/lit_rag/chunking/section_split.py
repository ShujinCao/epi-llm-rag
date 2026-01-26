from __future__ import annotations

import re
from typing import List, Tuple

# Very simple heading detection for v1.
# If you use GROBID, you'll get much cleaner section boundaries and can improve this.
HEADING_RE = re.compile(r"^(abstract|introduction|background|methods?|materials and methods|results?|discussion|conclusion|limitations|references)\b[:\s]*$", re.IGNORECASE)

def split_into_sections(text: str) -> List[Tuple[str, str]]:
    lines = [ln.strip() for ln in text.splitlines()]
    sections: List[Tuple[str, List[str]]] = []
    cur_name = "Unknown"
    cur_buf: List[str] = []

    def flush():
        nonlocal cur_buf, cur_name
        if cur_buf:
            sections.append((cur_name, cur_buf))
            cur_buf = []

    for ln in lines:
        if not ln:
            continue
        if len(ln) < 60 and HEADING_RE.match(ln.lower()):
            flush()
            cur_name = ln.strip().title()
            continue
        cur_buf.append(ln)

    flush()
    return [(name, "\n".join(buf)) for name, buf in sections]
