from __future__ import annotations

from typing import List, Dict, Any
from openai import OpenAI

from lit_rag.config import settings
from lit_rag.index.schema import PrevalenceIncidenceExtraction
from lit_rag.rag.prompt_templates import SYSTEM, user_prompt, build_evidence_pack

# JSON Schema for Structured Outputs (Pydantic-like but explicit)
EXTRACTION_SCHEMA: Dict[str, Any] = {
  "name": "prevalence_incidence_extraction",
  "schema": {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "condition": {"type": "string"},
      "metric_type": {"type": "string", "description": "prevalence | incidence"},
      "value": {"type": "string", "description": "Numeric value as written, e.g. '10.5%'. Empty if not found."},
      "unit": {"type": "string", "description": "percentage | per 100,000 | per 1,000 | other"},
      "population": {"type": "string"},
      "location": {"type": "string"},
      "year_range": {"type": "string"},
      "study_type": {"type": "string"},
      "confidence": {"type": "string", "description": "high | medium | low"},
      "sources": {
        "type": "array",
        "items": {
          "type": "object",
          "additionalProperties": False,
          "properties": {
            "paper_id": {"type": "string"},
            "chunk_id": {"type": "string"},
            "section": {"type": "string"},
            "quote": {"type": "string"}
          },
          "required": ["paper_id", "chunk_id", "quote"]
        }
      }
    },
    "required": ["condition","metric_type","value","unit","population","location","year_range","study_type","confidence","sources"]
  },
  "strict": True
}

class Extractor:
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY missing. Set it in backend/.env")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def extract(self, question: str, hits) -> PrevalenceIncidenceExtraction:
        evidence = build_evidence_pack(hits)
        prompt = user_prompt(question, evidence)

        resp = self.client.responses.create(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            input=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "json_schema": EXTRACTION_SCHEMA
                }
            },
            store=False,
        )

        # The SDK returns output_text for text responses; for structured outputs,
        # it's still delivered as text containing JSON that matches the schema.
        raw = resp.output_text
        extraction = PrevalenceIncidenceExtraction.model_validate_json(raw)
        return extraction
