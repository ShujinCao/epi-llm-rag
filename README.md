# Literature-RAG for Prevalence & Incidence Extraction
A Retrieval-Augmented Generation (RAG) pipeline for automatically extracting epidemiological indicators (prevalence, incidence, measurement years, uncertainty) from global health literature using transformer embeddings and GPT-5.

Production Architecture:
```
• BERT sentence embeddings (or E5-large-v2 for higher accuracy)
• FAISS vector search
• GPT-5 for structured information extraction from retrieved texts
• FastAPI for deployment
• AWS for scalable compute
```
## Structure

```
epi-llm-rag/
│
├── data/
│   ├── sample_papers/       # A few open-access abstracts
│   └── annotations/         # Example extracted prevalence data
│
├── notebooks/
│   ├── 01_embedding.ipynb
│   ├── 02_rag_pipeline.ipynb
│   ├── 03_extraction_gpt5.ipynb
│   └── 04_evaluation.ipynb
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
