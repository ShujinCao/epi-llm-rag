from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
import requests
import fitz  # PyMuPDF

from lit_rag.logging import get_logger
from lit_rag.config import settings

log = get_logger(__name__)

@dataclass
class PaperDoc:
    paper_id: str
    source: str
    title: Optional[str]
    year: Optional[int]
    text: str
    meta: Dict[str, Any]

def _pymupdf_extract(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(doc.page_count):
        pages.append(doc.load_page(i).get_text("text"))
    return "\n".join(pages)

def _grobid_extract(pdf_path: Path) -> str:
    # Uses GROBID service /api/processFulltextDocument
    # NOTE: returns TEI XML; for v1 we do a basic strip.
    url = settings.grobid_url.rstrip("/") + "/api/processFulltextDocument"
    with pdf_path.open("rb") as f:
        files = {"input": (pdf_path.name, f, "application/pdf")}
        r = requests.post(url, files=files, timeout=120)
    r.raise_for_status()
    tei = r.text
    # Basic: drop tags; keep content
    import re
    text = re.sub(r"<[^>]+>", "", tei)
    return text

def pdf_to_text(pdf_path: Path) -> str:
    if settings.use_grobid:
        try:
            return _grobid_extract(pdf_path)
        except Exception as e:
            log.warning("GROBID failed for %s (%s). Falling back to PyMuPDF.", pdf_path, e)
    return _pymupdf_extract(pdf_path)
