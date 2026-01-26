from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List
from tqdm import tqdm

from lit_rag.config import settings
from lit_rag.logging import get_logger
from lit_rag.ingest.pdf_to_text import pdf_to_text
from lit_rag.ingest.normalize import normalize_text
from lit_rag.ingest.metadata import infer_title_from_filename, infer_year_from_filename
from lit_rag.chunking.chunker import Chunker
from lit_rag.index.schema import Chunk
from lit_rag.embed.e5 import E5Embedder
from lit_rag.index.faiss_store import build_index, save_bundle

log = get_logger(__name__)

def cmd_ingest(args):
    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted([p for p in in_dir.rglob("*.pdf")])
    if not pdfs:
        raise SystemExit(f"No PDFs found under {in_dir}")

    for pdf in tqdm(pdfs, desc="Ingest PDFs"):
        rel = pdf.relative_to(in_dir)
        paper_id = rel.stem
        source = rel.parts[0] if len(rel.parts) > 1 else "other"
        title = infer_title_from_filename(pdf)
        year = infer_year_from_filename(pdf)

        text = pdf_to_text(pdf)
        text = normalize_text(text)

        doc = {
            "paper_id": paper_id,
            "source": source,
            "title": title,
            "year": year,
            "text": text,
            "meta": {"path": str(rel)}
        }
        out_path = out_dir / (paper_id + ".json")
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

def cmd_chunk(args):
    in_dir = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    docs = sorted(in_dir.glob("*.json"))
    if not docs:
        raise SystemExit(f"No ingested docs found under {in_dir}")

    chunker = Chunker()
    with out_path.open("w", encoding="utf-8") as f:
        for p in tqdm(docs, desc="Chunk docs"):
            doc = json.loads(p.read_text(encoding="utf-8"))
            chunks = chunker.chunk_text(
                paper_id=doc["paper_id"],
                source=doc.get("source","other"),
                title=doc.get("title"),
                year=doc.get("year"),
                text=doc["text"]
            )
            for c in chunks:
                f.write(c.model_dump_json())
                f.write("\n")

def cmd_index(args):
    chunks_path = Path(args.chunks)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks: List[Chunk] = []
    texts: List[str] = []
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c = Chunk.model_validate_json(line)
                chunks.append(c)
                texts.append(c.text)

    embedder = E5Embedder(settings.e5_model)
    vecs = embedder.embed_passages(texts, batch_size=args.batch_size)
    bundle = build_index(chunks, vecs)
    save_bundle(bundle, out_dir)
    log.info("Saved FAISS index to %s", out_dir)

def build_parser():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("ingest")
    p1.add_argument("--in", dest="input", required=True)
    p1.add_argument("--out", dest="output", required=True)
    p1.set_defaults(fn=cmd_ingest)

    p2 = sub.add_parser("chunk")
    p2.add_argument("--in", dest="input", required=True)
    p2.add_argument("--out", dest="output", required=True)
    p2.set_defaults(fn=cmd_chunk)

    p3 = sub.add_parser("index")
    p3.add_argument("--chunks", required=True)
    p3.add_argument("--out", dest="output", required=True)
    p3.add_argument("--batch-size", type=int, default=32)
    p3.set_defaults(fn=cmd_index)

    return ap

def main():
    ap = build_parser()
    args = ap.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
