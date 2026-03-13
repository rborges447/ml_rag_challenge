# ML RAG Challenge

API RAG com FastAPI: ingestão de PDFs (pré-processamento + LangChain + Chroma), retrieval em duas etapas (busca ampla + reranking heurístico) e geração de resposta final via LLM (Gemini e/ou OpenAI) usando contexto recuperado.



###############################################################################################################################################
## 1. Variáveis de ambiente (.env)
###############################################################################################################################################

O projeto usa variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto antes de rodar a API ou a UI.

1. **Copie o exemplo para `.env`:**

   ```bash
   # Windows (PowerShell)
   copy .env.example .env

   # Linux/macOS
   cp .env.example .env
   ```

2. **Edite o `.env`** e preencha pelo menos:

   - **`GEMINI_API_KEY`** – chave da API do Google (Gemini), necessária para usar modelos Gemini. Obtenha em [Google AI Studio](https://aistudio.google.com/apikey).
   - **`OPENAI_API_KEY`** – chave da API da OpenAI, necessária para usar modelos OpenAI (ex.: `gpt-4.1-mini`). Obtenha em [OpenAI API keys](https://platform.openai.com/api-keys).
   - **`LLM_ROUTE`** – cadeia de modelos e providers usada pelo `LLMClient` para fallback (veja abaixo **Roteamento e prioridade de modelos (LLM_ROUTE)**).
   - **`API_BASE_URL`** – URL da API que a UI vai chamar (em desenvolvimento local, normalmente `http://localhost:8000`).
   - As demais variáveis têm valores padrão no `.env.example`; altere apenas se precisar (por exemplo, paths de dados).

3. **Não versionar o `.env`** – ele contém dados sensíveis. O `.env.example` serve só de modelo (sem chaves reais).

### Roteamento e prioridade de modelos (LLM_ROUTE)

A variável `LLM_ROUTE` define **a ordem de tentativa entre modelos** (fallback) usada pelo `LLMClient`.

- Formato geral:  
  `LLM_ROUTE=provider:model,provider:model,...`
- A **ordem** representa a **prioridade**: o primeiro da lista é tentado primeiro, depois o segundo, e assim por diante até um provider funcionar.

Exemplo do `.env.example`:

```bash
LLM_ROUTE=gemini:gemini-3-flash,gemini:gemini-3-flash-preview,gemini:gemini-2.5-flash,openai:gpt-4.1-mini
```

Exemplos de configurações:

- **Somente Gemini**:
  ```bash
  LLM_ROUTE=gemini:gemini-3-flash
  ```
- **Somente OpenAI**:
  ```bash
  LLM_ROUTE=openai:gpt-4.1-mini
  ```
- **Priorizar OpenAI com fallback em Gemini**:
  ```bash
  LLM_ROUTE=openai:gpt-4.1-mini,gemini:gemini-3-flash
  ```

Para alterar a prioridade, **basta mudar a ordem em `LLM_ROUTE`**, sem alterar código.



###############################################################################################################################################
## 2. Rodando com Docker (API + UI)
###############################################################################################################################################

**Pré-requisito:** Docker e Docker Compose instalados.

Passos:

1. Garanta que o `.env` foi criado e preenchido (ver seção **1. Variáveis de ambiente (.env)**).

2. Na raiz do projeto, suba os serviços:

   ```bash
   docker compose up -d
   # ou, dependendo da versão:
   docker-compose up -d
   ```

3. **Acessos:**
   - API: http://localhost:8000 (docs: http://localhost:8000/docs)
   - UI: http://localhost:8501

4. Para parar os serviços:

   ```bash
   docker compose down
   ```

Observações:

- Dentro do Docker, a UI usa `API_BASE_URL=http://api:8000` (nome do serviço no compose).
- Os dados (Chroma e uploads) persistem no volume `rag_data`; em novo `up`, o índice e os PDFs enviados continuam disponíveis.
- **Não é necessário rodar `pip install -r requirements.txt` para o fluxo com Docker.**



###############################################################################################################################################
## 3. Rodando sem Docker (local)
###############################################################################################################################################
   
   ############################################################################################################################################
   ### 3.1 Ambiente virtual e dependências
   ############################################################################################################################################

   Na raiz do projeto, recomenda-se usar um ambiente virtual e instalar as dependências com:

   ```bash
   # Criar venv
   python -m venv .venv

   # Ativar venv
   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # Linux/macOS
   source .venv/bin/activate

   # Instalar dependências
   pip install -r requirements.txt
   ```
   ############################################################################################################################################
   ### 3.2 API FastAPI
   ############################################################################################################################################

   Depois do venv ativo, para subir a API:

   - **Linux/macOS**:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   - **Windows (evita erro `[WinError 10013]`)**:

   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

   Em desenvolvimento, a flag `--reload` recarrega automaticamente ao alterar o código.

   Documentação interativa: http://localhost:8000/docs

   ############################################################################################################################################
   ### 3.3 Interface Streamlit (chat)
   ############################################################################################################################################

   A UI consome a API apenas via HTTP. Rode API e UI em **processos separados** (dois terminais):

   1. **Terminal 1 – API:** comando `uvicorn` conforme seção anterior (por exemplo, em Windows `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`).
   2. **Terminal 2 – UI:** `streamlit run ui/streamlit_app.py`

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


###############################################################################################################################################
## Reindexação
###############################################################################################################################################

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


###############################################################################################################################################
### Backend – paths
###############################################################################################################################################

- `CHROMA_PATH` (default `data/chroma`) – diretório do banco vetorial Chroma.
- `UPLOAD_DIR` (default `data/raw`) – diretório onde os PDFs enviados são salvos.


###############################################################################################################################################
### Chunking
###############################################################################################################################################

- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `INTRO_PAGE_MAX`


###############################################################################################################################################
### Retrieval
###############################################################################################################################################

- `RETRIEVAL_INITIAL_K`
- `RETRIEVAL_TOP_K_FINAL`
- `RETRIEVAL_MAX_DISTANCE`
- `RETRIEVAL_MIN_SCORE`


###############################################################################################################################################
### LLM
###############################################################################################################################################

- `LLM_TIMEOUT_SECONDS` – timeout máximo para resposta do modelo (segundos).
- `LLM_ROUTE` – cadeia de modelos/providers e ordem de prioridade (veja seção específica acima).
- `GEMINI_API_KEY` – chave da API Gemini.
- `GEMINI_MODEL` – modelo default Gemini (ex.: `gemini-3-flash-preview`).
- `OPENAI_API_KEY` – chave da API OpenAI.



###############################################################################################################################################
### UI
###############################################################################################################################################

- `API_BASE_URL` – URL da API (ex.: `http://localhost:8000` em uso local ou `http://api:8000` em Docker Compose).
- `UI_HTTP_TIMEOUT_SECONDS` – timeout das chamadas HTTP da UI para a API.
