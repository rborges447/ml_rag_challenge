<div align="center">

# 📄 RAG API & UI

### Question-and-Answer System for PDF Documents

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange?style=flat)](https://www.trychroma.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

**End-to-end RAG pipeline** — upload PDFs, ask questions in natural language, get answers grounded in your documents.

[Quick Start](#-quick-start-3-minutes) · [How It Works](#️-how-it-works) · [API Reference](#-api-reference) · [Project Structure](#-project-structure)

</div>

---

## 🧠 What Is This Project?

A production-grade **Retrieval-Augmented Generation (RAG)** system: instead of relying on a language model's general knowledge, it reads your PDFs, indexes their content in a vector database, and generates answers sourced directly from the documents — with exact references included.

| Layer | Technology |
|---|---|
| **Back-end API** | FastAPI |
| **Vector Store** | ChromaDB |
| **Embeddings** | HuggingFace Sentence Transformers |
| **LLM Providers** | Google Gemini · OpenAI (automatic fallback) |
| **UI** | Streamlit |
| **Infra** | Docker Compose |

---

## ✨ Key Features

- **📥 PDF Ingestion Pipeline** — text extraction → cleaning → chunking → embedding → vector storage
- **🔍 Semantic Search** — vector similarity retrieval with heuristic reranking
- **🔄 Query Expansion (EN → PT)** — expands English technical terms to Portuguese equivalents for multilingual documents
- **🧹 Chunk Deduplication** — removes redundant context before sending to the LLM
- **⚡ LLM Fallback** — automatically switches between Gemini and OpenAI if a provider fails
- **🖥️ Web UI** — upload documents and chat via a clean Streamlit interface
- **📖 Interactive Docs** — Swagger UI available out of the box at `/docs`

---

## 🚀 Quick Start (3 minutes)

**Prerequisites:** Docker and at least one API key (Gemini or OpenAI).

```bash
# 1. Clone the repository
git clone https://github.com/rborges447/ml_rag_challenge
cd ml_rag_challenge

# 2. Configure environment variables
cp .env.example .env
# Edit .env and add your key(s):
#   GEMINI_API_KEY=your_key_here
#   OPENAI_API_KEY=your_key_here

# 3. Build and start all services
docker compose up --build
```

> **Daily use** (skip the build): `docker compose up -d`

Once running, open the services:

| Service | URL | Description |
|---|---|---|
| Web Interface | http://localhost:8501 | Upload PDFs and chat |
| API | http://localhost:8000 | Main back-end |
| Swagger Docs | http://localhost:8000/docs | Interactive API explorer |

---

## 📖 Usage

### Via the Web Interface

1. Open [http://localhost:8501](http://localhost:8501)
2. Upload one or more PDF files
3. Navigate to the **Chat** page
4. Ask your question — receive an answer with document references

### Via the API (curl)

```bash
# Health check
curl http://localhost:8000/health

# Upload a document
curl -X POST http://localhost:8000/documents \
  -F "file=@document.pdf"

# Ask a question
curl -X POST http://localhost:8000/question \
  -H "Content-Type: application/json" \
  -d '{"question": "What is an induction motor?"}'
```

---

## 💡 Example Q&A

Sample PDFs are included in `example_data/`. Upload them and try:

> **Q:** How often should motor bearings be lubricated for motors up to frame size 210 at 1800 RPM?  
> **A:** Motor bearings should be relubricated every 12,000 hours.

> **Q:** What lubricant is recommended for new Baldor submersible motors?  
> **A:** Shell Rotella SAE 10W. New motors ship with the oil reservoir properly filled.

> **Q (Portuguese doc):** Why is the induction motor the most used type of electric motor?  
> **A:** Simple construction, high reliability, low cost, low maintenance and good efficiency.

---

## 🏗️ How It Works

The system runs two independent pipelines:

```
Ingestion   PDF ──► Text Extraction ──► Cleaning ──► Chunking ──► Embeddings ──► ChromaDB

Questions   Query ──► Embedding ──► Vector Search ──► Reranking ──► Prompt ──► LLM ──► Answer
```

### Technical Highlights

**Query Expansion** — Translates English technical terms into Portuguese equivalents at retrieval time, improving recall on bilingual corpora without reindexing.

**Heuristic Reranking** — Detects conceptual queries ("why", "advantages", "how does it work") and boosts chunks from introductory sections, where definitions tend to appear.

**Chunk Deduplication** — Removes near-duplicate chunks before building the LLM prompt, reducing noise and staying within token limits.

**Provider Fallback** — Gemini and OpenAI are used interchangeably; if one fails, the system retries with the other transparently.

---

## 📁 Project Structure

```
├── app/
│   ├── api/                # FastAPI route handlers
│   ├── pipelines/          # Ingestion and question pipelines
│   ├── retrieval/          # Vector search and reranking
│   ├── document_processor/ # PDF text extraction and chunking
│   ├── storage/            # Vector DB abstraction layer
│   ├── qa/                 # Prompt construction
│   ├── clients/            # LLM provider clients (Gemini, OpenAI)
│   └── core/               # Config, logging, dependency injection
│
├── ui/
│   ├── pages/              # Streamlit pages
│   ├── components/         # Reusable UI components
│   └── services/           # API communication layer
│
├── scripts/
│   └── exemple_questions.py
│
├── example_data/           # Sample PDFs for testing
├── docker-compose.yml
└── .env.example
```

---

## 🔧 Running Without Docker

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Start the API (terminal 1)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start the UI (terminal 2)
streamlit run ui/streamlit_app.py
```

---

## 🛠️ Troubleshooting

**No LLM provider available**
Make sure `.env` contains at least one valid key:
```
GEMINI_API_KEY=your_key
# or
OPENAI_API_KEY=your_key
```

**Poor retrieval quality**
- Re-upload documents if they weren't indexed correctly
- If you changed the embedding model, reindex all documents
- Verify the uploaded PDFs are related to your questions

**Services won't start**
```bash
docker ps                        # confirm Docker is running
docker compose logs api ui       # inspect per-service logs
```
> Make sure ports `8000` and `8501` are free before starting.

---

## 📋 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/documents` | Upload a PDF file |
| `POST` | `/question` | Ask a question (JSON body: `{"question": "..."}`) |

Full interactive documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

<div align="center">

Built with focus on **retrieval quality**, **modular architecture**, and **developer experience**.

</div>

