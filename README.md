# Literature-RAG for Prevalence & Incidence Extraction
A Retrieval-Augmented Generation (RAG) pipeline for automatically extracting epidemiological indicators (prevalence, incidence, measurement years, uncertainty) from global health literature using transformer embeddings and GPT-4.

Production Architecture:
```
• E5-large-v2 embeddings 
• FAISS vector search
• GPT-4 for structured information extraction from retrieved texts
• FastAPI for deployment
• AWS for scalable compute
```
### Preprocessing pipeline
PDF
 → GROBID
 → sectioned text
 → clean normalization
 → chunking
 → embedding

## Structure

```
epi-llm-rag/
│
├── notebooks/
│  
├── src/
│   ├── retriever/
│   │   ├── embedder.py      # E5 or BioBERT embeddings
│   │   ├── vector_store.py  # FAISS or OpenSearch
│   │   └── rag_retrieve.py
│   │
│   ├── extractor/
│       ├── extractor_gpt5.py  # GPT-5 extraction code
│       └── prompt_templates.py
│
├── configs/
│   └── rag_config.yaml
│
├── app/
│   └── api.py               # FastAPI endpoint for query → extraction
│
├── requirements.txt
└── README.md
```
