from __future__ import annotations

import argparse
from pathlib import Path
import requests
import yaml
from tqdm import tqdm

def download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)

def safe_name(url: str) -> str:
    import re
    name = url.split("?")[0].rstrip("/").split("/")[-1]
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name)
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True, help="YAML with urls list")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    seeds = yaml.safe_load(Path(args.seeds).read_text(encoding="utf-8"))
    urls = seeds.get("urls", [])
    out_dir = Path(args.out)

    for url in tqdm(urls, desc="Downloading seed PDFs"):
        try:
            download(url, out_dir / safe_name(url))
        except Exception:
            continue

    print(f"Done. Output: {out_dir}")

if __name__ == "__main__":
    main()
