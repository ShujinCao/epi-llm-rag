from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional
import time
import requests
from tqdm import tqdm

# Uses:
# - NCBI E-utilities to search PMC
# - PMC OA Web Service API to locate PDFs (Open Access subset)
#
# Note: this is a pragmatic v1 implementation. For production, add caching and stronger error handling.

NCBI_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PMC_OA_API = "https://pmc.ncbi.nlm.nih.gov/tools/oa-service/"

def esearch_pmc_ids(query: str, retmax: int = 50) -> List[str]:
    params = {
        "db": "pmc",
        "term": query,
        "retmode": "json",
        "retmax": str(retmax),
        "sort": "relevance",
    }
    r = requests.get(NCBI_ESEARCH, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    return js["esearchresult"].get("idlist", [])

def oa_pdf_url(pmcid: str) -> Optional[str]:
    # OA service supports ?id=PMCxxxx
    r = requests.get(PMC_OA_API, params={"id": pmcid}, timeout=30)
    r.raise_for_status()
    # It's XML; look for <link format="pdf" href="...">
    import re
    m = re.search(r'format="pdf"\s+href="([^"]+)"', r.text)
    if not m:
        return None
    href = m.group(1)
    if href.startswith("http"):
        return href
    return "https://pmc.ncbi.nlm.nih.gov" + href

def download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="PMC search query (Entrez syntax)")
    ap.add_argument("--max", type=int, default=50, help="Max PDFs to download")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    out_dir = Path(args.out)
    ids = esearch_pmc_ids(args.query, retmax=args.max * 3)  # overfetch; many won't have OA PDFs
    got = 0

    for pmc_uid in tqdm(ids, desc="Resolving PMCIDs"):
        pmcid = f"PMC{pmc_uid}"
        pdf = oa_pdf_url(pmcid)
        if not pdf:
            continue
        try:
            download(pdf, out_dir / f"{pmcid}.pdf")
            got += 1
        except Exception:
            continue
        time.sleep(0.2)
        if got >= args.max:
            break

    print(f"Downloaded {got} PDFs to {out_dir}")

if __name__ == "__main__":
    main()
