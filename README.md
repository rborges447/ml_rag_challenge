📄 RAG API & UI
Question-and-Answer System for PDF Documents

FastAPI • ChromaDB • HuggingFace • Gemini / OpenAI • Streamlit

🤔 What is this project?
This project is a complete RAG (Retrieval-Augmented Generation) system — an AI technique that lets you ask questions about PDF documents and receive accurate answers based on the actual content of the files.

Instead of an AI that "guesses" answers, this system reads your documents, indexes the content and then answers — with references to the exact excerpt the answer came from.

🧠 What it does: Answers questions about PDF documents using AI
⚙️ Back-end: FastAPI + ChromaDB + HuggingFace Embeddings
🖥️ Interface: Streamlit — simple and visual
🤖 AI: Google Gemini or OpenAI (with automatic fallback)
🐳 Deploy: Docker Compose — brings everything up with one command

🚀 Quick Start (3 minutes)
Prerequisites
Docker installed on the machine
Google Gemini or OpenAI API key (at least one)

Step 1 — Clone the repository
git clone 
cd ml_rag_challenge

Step 2 — Configure environment variables
cp .env.example .env
Open the .env file and add at least one API key:

GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

Tip: Only one key is required. If you configure both, the system uses automatic fallback between providers.

Step 3 — Start the services

First time (or after changing requirements.txt / base image)
docker compose up --build

Daily use (faster, reuses built image)
docker compose up -d
Wait for the build to finish. The first run may take a few minutes (especially while installing dependencies).

Available services
Service URL Description
API http://localhost:8000 Main back-end
Swagger Docs http://localhost:8000/docs Interactive API documentation
Web Interface http://localhost:8501 UI for upload and questions

📖 How to use
Via the web interface (Streamlit)
Open http://localhost:8501 in your browser
Upload one or more PDF documents
Go to the Chat page
Ask your question and receive the answer with document references

Via the API
Method Endpoint Description
GET /health Checks if the API is running
POST /documents Upload a PDF
POST /question Ask a question

Health check
curl http://localhost:8000/health

Upload document
curl -X POST http://localhost:8000/documents 
  -F "file=@document.pdf"

Ask a question
curl -X POST http://localhost:8000/question 
  -H "Content-Type: application/json" 
  -d '{"question": "What is an induction motor?"}'

💡 Example questions and answers
Sample PDFs are in the example_data/ folder. Upload and test:

LB5001.pdf

❓ How often should motor bearings be lubricated for motors up to frame size 210 at 1800 RPM? ✅ Motor bearings should be relubricated every 12,000 hours.

MN414_0224.pdf

❓ What lubricant is recommended for new Baldor submersible motors? ✅ Shell Rotella SAE 10W. New motors ship with the oil reservoir properly filled.

WEG-CESTARI manual

❓ Within what maximum period must WEG-CESTARI gear units be put into operation after leaving the factory? ✅ Within a maximum period of 6 months after leaving the factory.

WEG motor (in Portuguese)

❓ Why is the induction motor the most used type of electric motor? ✅ Simple construction, high reliability, low cost, low maintenance and good efficiency.

Note: Exact wording of the answer may vary depending on the LLM provider, but the key information should match.

Run example questions via Docker (scripts/exemples_questions.py)

Create and run a new container
docker compose run --rm api python scripts/exemples_questions.py

Or, if the stack is already up with docker compose up
docker compose exec api python scripts/exemples_questions.py

🏗️ How the system works
The system operates in two pipelines:

Ingestion (PDF upload)
PDF → text extraction → cleaning → chunking → embeddings → ChromaDB

Questions
question → embedding → vector search → reranking → prompt → LLM → answer

⚙️ Technical highlights
Query Expansion (EN → PT)
Technical English terms are expanded to Portuguese equivalents, improving retrieval when the question is in English but the document is in Portuguese.

Heuristic Reranking
Conceptual questions ("why", "advantages", "how does it work") tend to appear in introductory sections. The reranker detects this pattern and adjusts chunk scores.

Chunk Deduplication
Very similar chunks are removed before being sent to the LLM, avoiding redundant context.

Fallback between LLM providers
If the primary provider fails, the system automatically tries the secondary provider — with no interruption for the user.

📁 Project structure
app/ ├── api/ # FastAPI routes ├── pipelines/ # Ingestion and question pipelines ├── retrieval/ # Search and reranking ├── document_processor/ # PDF processing ├── storage/ # Vector DB abstraction ├── qa/ # Prompt construction ├── clients/ # LLM providers └── core/ # Config, logging, dependencies

ui/ ├── pages/ # Interface pages ├── components/ # Reusable components └── services/ # API communication

scripts/ └── exemple_questions.py

🛠️ Running without Docker (optional)
1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / Mac
.venv\Scripts\activate         # Windows

2. Install dependencies
pip install -r requirements.txt

3. Start the API
uvicorn app.main:app --host 0.0.0.0 --port 8000

4. Start the interface (in another terminal)
streamlit run ui/streamlit_app.py

🔧 Troubleshooting
No LLM provider available Check that .env contains at least one key:

GEMINI_API_KEY=your_key

or
OPENAI_API_KEY=your_key

Poor retrieval quality
Documents were not indexed — re-upload them
The embedding model was changed — reindex documents
Documents unrelated to the question — check uploaded files

Services won't start with Docker
docker ps                          # check that Docker is running
docker compose logs api ui         # inspect logs for each service

Tip: Use docker compose up --build only when changing dependencies (e.g., requirements.txt) or the base image. For daily use prefer docker compose up -d, which is much faster by reusing built images. Also confirm ports 8000 and 8501 are not in use.

Built with focus on retrieval quality, modular architecture and developer experience.
