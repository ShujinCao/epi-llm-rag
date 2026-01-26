from __future__ import annotations

SYSTEM = """You are an epidemiology research assistant. 
You MUST only use the provided passages as evidence.
If the passages do not contain an explicit prevalence/incidence statement, you must return confidence='low' and leave value as an empty string.
Always include at least one source quote when confidence is medium/high.
Prefer the most recent year range that matches the question.
"""

def build_evidence_pack(hits):
    # compact, citation-friendly pack
    # Each passage has a stable citation key: [chunk_id]
    parts = []
    for h in hits:
        header = f"[chunk_id={h.chunk_id}] paper_id={h.paper_id} source={h.source} year={h.year} section={h.section} title={h.title}"
        parts.append(header + "\n" + h.text.strip())
    return "\n\n---\n\n".join(parts)

def user_prompt(question: str, evidence_pack: str) -> str:
    return f"""Question:
{question}

Evidence passages (use ONLY these):
{evidence_pack}

Task:
Extract prevalence/incidence as structured JSON per the provided schema.
""""
