from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))

    e5_model: str = os.getenv("E5_MODEL", "intfloat/e5-large-v2")

    grobid_url: str = os.getenv("GROBID_URL", "http://localhost:8070")
    use_grobid: bool = os.getenv("USE_GROBID", "true").lower() in ("1", "true", "yes", "y")

    data_dir: str = os.getenv("DATA_DIR", "../data")

settings = Settings()
