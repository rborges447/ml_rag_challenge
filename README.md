# ML RAG Challenge

API RAG com FastAPI: ingestão de PDFs (pré-processamento + LangChain + Chroma), retrieval em duas etapas (busca ampla + reranking heurístico) e geração de resposta final via LLM (Gemini) usando contexto recuperado.

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração do ambiente (.env)

O projeto usa variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto antes de rodar a API ou a UI.

1. **Copie o exemplo para `.env`:**
   ```bash
   copy .env.example .env
   ```
   (No Linux/macOS: `cp .env.example .env`.)

2. **Edite o `.env`** e preencha pelo menos:
   - **`GEMINI_API_KEY`** – chave da API do Google (Gemini), necessária para o fluxo de perguntas e respostas. Obtenha em [Google AI Studio](https://aistudio.google.com/apikey).
   - As demais variáveis têm valores padrão no `.env.example`; altere apenas se precisar (por exemplo, outra URL da API para a UI ou paths diferentes).

3. **Não versionar o `.env`** – ele contém dados sensíveis. O `.env.example` serve só de modelo (sem chaves reais).

## Rodar a API

Na raiz do projeto:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Em desenvolvimento, use `--reload` para recarregar ao alterar o código.

Documentação interativa: http://localhost:8000/docs

## Interface Streamlit (chat)

A UI consome a API apenas via HTTP. Rode API e UI em **processos separados** (dois terminais):

1. **Terminal 1 – API:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. **Terminal 2 – UI:** `streamlit run ui/streamlit_app.py`

Dependências (streamlit e httpx) já estão em `requirements.txt`.

Na interface Streamlit:

- Use a sidebar para configurar a URL da API (default `http://localhost:8000`) e fazer upload de PDFs.
- Use a área principal de chat para enviar perguntas no formato:
  - `Q: "sua pergunta"`
  - `A: "resposta gerada pela LLM com base nos documentos indexados"`

## Testes rápidos

1. **Indexar um PDF**: `POST /documents` com um arquivo PDF (form-data, campo `file`).
2. **Testar perguntas com LLM**: `POST /question` com body `{"question": "sua pergunta"}`. A resposta traz:
   - `answer`: resposta em linguagem natural vinda da LLM.
   - `references`: lista de referências simples baseadas em `source/page`.
   - `retrieved_chunks`: lista de chunks usados como contexto (para debug).
3. **Query params** (opcionais): `top_k` (chunks finais, default 5), `initial_k` (candidatos antes do rerank), `max_distance` (filtro L2).

## Reindexação

Após mudanças no pré-processamento, chunking ou embedding, o índice antigo não reflete a nova estratégia. Para reindexar:

1. Pare a API.
2. Apague o diretório `data/chroma` (ou o path em `CHROMA_PATH`).
3. Suba a API e reenvie os PDFs via `POST /documents` para cada arquivo (os PDFs em `data/raw` continuam válidos; o serviço reextrai, pré-processa, rechunka e reindexa).

## Benchmark de retrieval

Script que avalia se o chunk relevante aparece no top-1, top-3 e top-5 para um conjunto de perguntas fixas (ex.: sobre motores elétricos).

**Pré-requisito:** Chroma já indexado (envie um PDF via `POST /documents` antes).

Execute a partir da raiz do projeto:

```bash
python scripts/benchmark_retrieval.py
```

A saída mostra, por pergunta, se houve acerto em top-1, top-3 e top-5 (critério: chunk contém os termos obrigatórios definidos no script).

## Variáveis de ambiente (referência)

Após criar o `.env` (ver seção **Configuração do ambiente (.env)** acima), você pode ajustar:

- **Backend – paths:** `CHROMA_PATH` (default `data/chroma`), `UPLOAD_DIR` (default `data/raw`).
- **Chunking:** `CHUNK_SIZE`, `CHUNK_OVERLAP`, `INTRO_PAGE_MAX`.
- **Retrieval:** `RETRIEVAL_INITIAL_K`, `RETRIEVAL_TOP_K_FINAL`, `RETRIEVAL_MAX_DISTANCE`, `RETRIEVAL_MIN_SCORE`.
- **LLM:** `LLM_PROVIDERS`, `LLM_TIMEOUT_SECONDS`, `GEMINI_API_KEY`, `GEMINI_MODEL` (obrigatório para Q&A).
- **UI:** `API_BASE_URL` (URL da API, ex.: `http://localhost:8000`), `UI_HTTP_TIMEOUT_SECONDS`.
