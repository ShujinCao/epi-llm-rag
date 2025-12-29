from __future__ import annotations

import re

def normalize_text(text: str) -> str:
    # Remove repeated whitespace
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    # Fix broken hyphenation at line breaks: "popu-\nlation" -> "population"
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Collapse many newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
