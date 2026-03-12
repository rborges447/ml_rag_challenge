# ML RAG Challenge

API RAG com FastAPI: ingestão de PDFs (pré-processamento + LangChain + Chroma), retrieval em duas etapas (busca ampla + reranking heurístico) e geração de resposta final via LLM (Gemini) usando contexto recuperado.

## Instalação

```bash
pip install -r requirements.txt
```

## Rodar a API

```bash
uvicorn app.main:app --reload
```

Documentação interativa: http://localhost:8000/docs

## Interface Streamlit (chat)

Para usar uma interface web simples (dark/clean) que consome a API:

1. Instale também as dependências opcionais:

```bash
pip install streamlit httpx
```

2. Rode a API e o Streamlit em processos separados (recomendado):

```bash
python run_api.py
streamlit run streamlit_app.py
```

Ou, para uma experiência rápida em desenvolvimento, use o script de conveniência que orquestra os dois:

```bash
python main.py
```

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

## Configuração relevante (.env ou variáveis de ambiente)

- **Chunking:** `CHUNK_SIZE` (default 1000), `CHUNK_OVERLAP` (default 200), `INTRO_PAGE_MAX` (páginas consideradas introdutórias).
- **Retrieval:** `RETRIEVAL_INITIAL_K` (candidatos no Chroma, default 30), `RETRIEVAL_TOP_K_FINAL` (chunks finais, default 5), `RETRIEVAL_MAX_DISTANCE`, `RETRIEVAL_MIN_SCORE`.
- **Chroma:** `CHROMA_PATH`, `CHROMA_COLLECTION_NAME`, `EMBEDDING_MODEL_NAME`.
