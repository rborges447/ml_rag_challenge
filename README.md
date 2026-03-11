# ML RAG Challenge

API RAG com FastAPI: ingestão de PDFs (LangChain + Chroma) e retrieval por similaridade. Sem geração de resposta por LLM (apenas chunks recuperados).

## Instalação

```bash
pip install -r requirements.txt
```

## Rodar a API

```bash
uvicorn app.main:app --reload
```

Documentação interativa: http://localhost:8000/docs

## Testes rápidos

1. **Indexar um PDF**: `POST /documents` com um arquivo PDF (form-data, campo `file`).
2. **Testar retrieval**: `POST /question` com body `{"question": "sua pergunta"}` e opcionalmente `top_k` e `max_distance` na query string. A resposta traz `retrieved_chunks` (text, source, page, distance, score).

## Reindexação

Após a refatoração para LangChain (ou qualquer mudança no chunking/embedding), o índice antigo não é compatível. Para reindexar:

1. Pare a API.
2. Apague o diretório `data/chroma` (ou o path configurado em `CHROMA_PATH`).
3. Suba a API e reenvie os PDFs via `POST /documents` para cada arquivo que deve estar no índice (os PDFs em `data/raw` continuam válidos; o serviço reextrai, rechunka e reindexa).
