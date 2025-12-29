from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple
import re

YEAR_RE = re.compile(r"(19\d{2}|20\d{2})")

def infer_year_from_filename(path: Path) -> Optional[int]:
    m = YEAR_RE.search(path.stem)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None

def infer_title_from_filename(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip()
