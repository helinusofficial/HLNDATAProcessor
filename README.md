# 🧠 AI-Ready Scientific Article Processing Pipeline for RAG Systems

AI-ready biomedical XML processing pipeline designed to transform large-scale research articles (e.g., PMC XML format) into clean, structured, high-signal datasets optimized for Retrieval-Augmented Generation (RAG) systems.


## 🚀 Overview

Modern RAG architectures require **high-quality, domain-filtered, noise-free corpora**.  
Raw scientific XML files (such as those from <https://www.ncbi.nlm.nih.gov/pmc/> PubMed Central (PMC)>) are:

- Structurally complex  
- Noisy (figures, references, tables, footnotes, formulas)  
- Inconsistent in formatting  
- Not embedding-ready  

This project solves that by:

- Parsing raw XML research articles  
- Applying domain-aware filtering logic  
- Cleaning and normalizing textual content  
- Extracting structured metadata  
- Storing curated articles in SQL Server  
- Preparing data for downstream embedding pipelines  

✅ **Result:** A clean biomedical knowledge base optimized for AI retrieval systems.


## 🧠 Designed for AI & RAG Systems

This pipeline is engineered for:

- LLM-powered medical assistants  
- Clinical decision support systems  
- Biomedical semantic search engines  
- Breast cancer knowledge retrieval systems  
- Vector database indexing  
- Embedding generation workflows  

### Filtering Strategy

The architecture separates:

❌ Non-target articles  
❌ Animal-only studies  
❌ Low-quality or incomplete records  

✅ Human breast-related research  
✅ Clean full-text scientific content  

### Impact on AI Systems

- Higher retrieval precision  
- Improved embedding semantic density  
- More reliable LLM answers  
- Better context relevance in RAG pipelines  


## 🔬 Intelligent Domain Filtering (Anti-Fake Logic)

A core innovation of this pipeline is **semantic domain filtering before ingestion**.

### 1️⃣ Breast-Specific Relevance Detection

Instead of naive keyword matching, the system uses:

- Context proximity rules (e.g., “breast” within 5 tokens of gland/cancer/cell/etc.)
- Cell line recognition (MCF-7, T47D, MDA-MB-231, etc.)
- Title-priority weighting
- Keyword + MeSH reinforcement

Prevents false positives like:

- “breast muscle exercise”
- “animal mammary models only”



### 2️⃣ Human vs Animal Study Detection

The system differentiates:

- Human clinical studies  
- Animal models (mouse, rat, zebrafish, etc.)  
- Veterinary contexts  

Articles are excluded if:

- They are animal-only studies  
- They lack human indicators  
- They are not breast-specific  

✅ Ensures strong alignment with **human breast research**, critical for medical AI systems.



## 🧹 Advanced Text Cleaning & Normalization

Multi-stage content sanitization:

### ✔ Removes

- Figures  
- Tables  
- Formulas  
- Footnotes  
- Acknowledgments  
- Supplementary materials  
- Reference sections  

### ✔ Cleans

- Null bytes (SQL-safe)  
- Extra whitespace  
- Broken formatting  
- Citation formatting inconsistencies  
- Inline reference spacing  
- Figure-only short sentences  

### ✔ Normalizes

- Paragraph separation (Windows-safe `\r\n\r\n`)  
- Reference markers (`[1]`, `(2-5)`, etc.)  
- Citation number ranges  
- Unicode inconsistencies  

✅ Output: **LLM-optimized clean scientific prose**



## 🧬 Structured Metadata Extraction

Each article is transformed into a structured model including:

- Title  
- Abstract (cleaned, paragraph-preserving)  
- Body text (reference-free)  
- Authors  
- Corresponding author + email  
- ORCID IDs  
- Affiliations  
- Journal metadata  
- DOI / PMID / PMC ID  
- Volume / Issue / Page range  
- Publication date  
- Funding sources  
- Ethics statement  
- License  
- MeSH terms  
- Keywords  
- Reference list (deduplicated)  

### Benefits

- Searchable  
- Traceable  
- Auditable  
- Scientifically reliable  



## 🏗 System Architecture

```text
XML Files (PMC)
        ↓
ProcessDataSrv
        ↓
Intelligent Filtering (Human + Breast)
        ↓
Full Metadata Extraction
        ↓
Text Cleaning & Normalization
        ↓
SQL Server Storage
        ↓
Embedding Pipeline
        ↓
Vector Database
        ↓
RAG System
```

---
## 💾 Database Integration

The system connects to **Microsoft SQL Server** and inserts processed records via stored procedure:

`InsertData`

### Tracks

- Duplicate DOI detection  
- Missing abstract or body  
- Non-target articles  
- Processing errors  
- Statistics logging  

✅ Ensures strong ingestion reliability for production environments.


## 📊 Logging & Reproducibility

Includes:

- Timestamped run folders  
- Deterministic random seeds  
- File-based logging  
- Console logging  
- Execution time tracking  
- Batch progress monitoring  

Designed for large-scale corpora (10K–100K+ XML files).


## 🔄 Why This Matters for RAG

In Retrieval-Augmented Generation systems:

> Garbage in = Hallucinations out

This project ensures:

- Domain purity  
- Human-specific biomedical focus  
- Clean semantic chunks  
- Reliable citation metadata  
- SQL-safe structured storage  

### Direct Improvements

- Higher embedding quality  
- Better retrieval accuracy  
- Improved context precision  
- More grounded LLM responses  
- Reduced hallucination risk  


## 🎯 Ideal Use Cases

- Breast cancer knowledge assistant  
- Biomedical Q&A chatbot  
- AI-powered literature review system  
- Clinical evidence retrieval engine  
- Research trend analysis  
- Scientific embedding generation platform  


## 🛠 Tech Stack

- Python  
- lxml (robust XML recovery parsing)  
- Regex-based semantic filtering  
- Microsoft SQL Server  
- Logging framework  
- Structured Article Model  
- Deterministic reproducibility (NumPy, Torch seeds)  


## 🔒 Production-Oriented Design

- Fault-tolerant XML parsing  
- Recovery mode enabled  
- Deep copy of XML tree before mutation  
- Deduplicated references  
- SQL-safe string sanitation  
- Defensive error handling  
- Linearly scalable processing  


## 📈 Future Extensions

- Chunk-based segmentation for embeddings  
- Vector DB integration (FAISS, Milvus, Pinecone)  
- Automatic section labeling (Methods / Results / etc.)  
- NER extraction for biomedical entities  
- Citation graph construction  
- Hybrid keyword + vector retrieval  
- Automated embedding generation pipeline  


## 🧠 Philosophy

This is not just a parser.

It is a domain-aware AI data preparation engine built specifically for biomedical Retrieval-Augmented Generation systems.

Instead of blindly embedding raw scientific XML, it builds a:

- Curated  
- Human-focused  
- High-signal  
- AI-ready knowledge base  


## 📌 Summary

This repository provides:

- Intelligent XML parsing  
- Domain-specific filtering  
- Clean full-text extraction  
- Structured metadata modeling  
- SQL Server ingestion  
- RAG-ready biomedical corpus preparation  

Optimized for AI systems that demand structured, high-quality knowledge rather than noisy raw documents.
