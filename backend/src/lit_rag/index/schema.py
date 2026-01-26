from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List

class Chunk(BaseModel):
    chunk_id: str
    paper_id: str
    source: str = Field(description="pmc | who | cdc | other")
    title: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    text: str

class SearchHit(BaseModel):
    chunk_id: str
    paper_id: str
    score: float
    section: Optional[str] = None
    text: str
    title: Optional[str] = None
    year: Optional[int] = None
    source: Optional[str] = None

class ExtractSource(BaseModel):
    paper_id: str
    chunk_id: str
    section: Optional[str] = None
    quote: str

class PrevalenceIncidenceExtraction(BaseModel):
    condition: str
    metric_type: str = Field(description="prevalence | incidence")
    value: str = Field(description="Numeric value as written (e.g., '10.5%')")
    unit: str = Field(description="percentage | per 100,000 | per 1,000 | other")
    population: str
    location: str
    year_range: str
    study_type: str
    confidence: str = Field(description="high | medium | low")
    sources: List[ExtractSource]
