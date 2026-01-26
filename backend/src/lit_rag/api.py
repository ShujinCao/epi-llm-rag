from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from lit_rag.config import settings
from lit_rag.rag.retrieve import Retriever
from lit_rag.rag.extract import Extractor
from lit_rag.index.schema import SearchHit, PrevalenceIncidenceExtraction

app = FastAPI(title="Lit RAG Extractor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INDEX_DIR = Path(settings.data_dir) / "indexes"

def _get_retriever() -> Retriever:
    if not (INDEX_DIR / "index.faiss").exists():
        raise HTTPException(status_code=400, detail=f"FAISS index not found in {INDEX_DIR}. Run: cli index")
    return Retriever(INDEX_DIR)

class SearchRequest(BaseModel):
    query: str
    k: int = 8

class SearchResponse(BaseModel):
    hits: List[SearchHit]

class ExtractRequest(BaseModel):
    question: str = Field(..., description="Research question (prevalence/incidence)")
    k: int = 10

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/search", response_model=SearchResponse)
def search(req: SearchRequest):
    retriever = _get_retriever()
    hits = retriever.search(req.query, k=req.k)
    return SearchResponse(hits=hits)

@app.post("/api/extract", response_model=PrevalenceIncidenceExtraction)
def extract(req: ExtractRequest):
    retriever = _get_retriever()
    hits = retriever.search(req.question, k=req.k)
    extractor = Extractor()
    return extractor.extract(req.question, hits)
