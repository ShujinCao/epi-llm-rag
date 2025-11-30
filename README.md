# Literature-RAG for Prevalence & Incidence Extraction
A Retrieval-Augmented Generation (RAG) pipeline for automatically extracting epidemiological indicators (prevalence, incidence, measurement years, uncertainty) from global health literature using transformer embeddings and GPT-5.

Built with:
• BERT sentence embeddings (or E5-large-v2 for higher accuracy)
• FAISS vector search
• GPT-5 for structured information extraction from retrieved texts
• FastAPI for deployment
• AWS for scalable compute
