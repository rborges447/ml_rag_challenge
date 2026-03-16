# ML Engineering Challenge – RAG API & UI

## Descrição geral

Este projeto implementa um sistema completo de **RAG (Retrieval-Augmented Generation)** para perguntas e respostas sobre documentos PDF.  
A aplicação permite que usuários façam upload de documentos, que são processados, indexados em um vetor store (ChromaDB) e posteriormente utilizados para responder perguntas em linguagem natural com apoio de LLMs (Gemini e/ou OpenAI).

O sistema é composto por uma **API FastAPI** e uma **UI em Streamlit**, orquestrando um pipeline de ingestão de PDFs, geração de embeddings com modelos HuggingFace, recuperação de trechos relevantes (retrieval + rerank heurístico) e geração de respostas via LLMs com fallback entre providers. O foco é ser um backend/ML-engineering sólido, observável (logging estruturado) e pronto para experimentos de retrieval.

---

## Principais funcionalidades

- **Upload e ingestão de PDFs**
  - Upload de arquivos PDF pela API (`POST /documents`) ou via UI Streamlit.
  - Processamento de texto: limpeza, normalização, remoção de ruído, cabeçalhos/rodapés repetitivos.
  - Chunking dos documentos com `RecursiveCharacterTextSplitter`.
  - Enriquecimento de metadados (página, tamanho, flags de introdução, hints de seção).
  - Geração de embeddings usando modelos HuggingFace.
  - Armazenamento vetorial persistente no **ChromaDB**.

- **Perguntas e respostas (RAG)**
  - Endpoint para perguntas (`POST /question`).
  - Retrieval vetorial com ChromaDB + reranking heurístico sensível ao tipo de pergunta (ex.: “o que é …”).
  - Deduplicação de chunks similares.
  - Montagem de prompt contextualizado (com referências de origem/página).
  - Geração de resposta com LLM (Gemini / OpenAI) com estratégia de **fallback** entre múltiplos modelos.

- **UI Web (Streamlit)**
  - Tela de **upload** de múltiplos PDFs com feedback por arquivo.
  - Tela de **chat RAG** para realizar perguntas sobre os documentos indexados.
  - Visualização de **referências** e dos **chunks recuperados** (incluindo scores e trechos de texto).

- **Benchmark de retrieval**
  - Script `scripts/benchmark_retrieval.py` para avaliar a qualidade de retrieval em perguntas fixas, com métricas top-1/top-3/top-5.

- **Observabilidade**
  - Logging centralizado e consistente de pipelines (ingestão/pergunta) e operações de vector store.
  - `request_id` gerado por requisição para rastreabilidade ponta a ponta.

---

## Stack do projeto

- **Backend**
  - [FastAPI](https://fastapi.tiangolo.com/) (API HTTP)
  - [Pydantic / pydantic-settings](https://docs.pydantic.dev/latest/) (configuração)
  - [Uvicorn](https://www.uvicorn.org/) (servidor ASGI)
  - [ChromaDB](https://www.trychroma.com/) (vector store persistente)
  - [LangChain](https://python.langchain.com/)
    - `langchain-core`, `langchain-community`, `langchain-chroma`, `langchain-text-splitters`
  - [sentence-transformers](https://www.sbert.net/) (embeddings HuggingFace)
  - [PyMuPDF](https://pymupdf.readthedocs.io/) via `langchain_community.document_loaders.PyMuPDFLoader` (leitura de PDFs)

- **LLM Providers**
  - [Google Gemini](https://ai.google.dev/) via `google-genai`
  - [OpenAI](https://platform.openai.com/) via `openai` (nova API `responses`)

- **Frontend**
  - [Streamlit](https://streamlit.io/) (UI para upload e chat)

- **Infra / Dev**
  - Docker (imagens separadas para API e UI)
  - Docker Compose (orquestração API + UI + volume de dados)
  - `httpx` (cliente HTTP da UI para a API)

---

## Arquitetura do sistema

A arquitetura é organizada em camadas de domínio e infraestrutura dentro do diretório `app/`, com uma UI desacoplada em `ui/`.

### Componentes principais

- **API (FastAPI)**
  - `app/main.py`: inicialização da aplicação FastAPI, configuração de logging e rota `/health`.
  - `app/api/routes_documents.py`: rota de upload/ingestão de documentos.
  - `app/api/routes_questions.py`: rota de perguntas.
  - `app/api/schemas/`: schemas Pydantic usados pela API.

- **Pipelines**
  - `IngestionPipeline` (`app/pipelines/ingestion_pipeline.py`):  
    Orquestra `DocumentProcessingService` → `RetrievalService.embed_documents` → `VectorStore.add_vectors`.
  - `QuestionPipeline` (`app/pipelines/question_pipeline.py`):  
    Orquestra `RetrievalService.retrieve` → `QAService.build_prompt` → `LLMClient.generate` → montagem de referências.

- **Processamento de documentos (`app/document_processor/`)**
  - `DocumentLoaderService`: usa `PyMuPDFLoader` para carregar PDF e converter em lista de páginas (`{"page", "text"}`).
  - `TextPreprocessor`: normalização de texto, remoção de ruído/linhas inúteis, remoção de cabeçalhos/rodapés repetitivos e blocos genéricos.
  - `ChunkingService`: aplica `RecursiveCharacterTextSplitter` com `chunk_size` e `chunk_overlap` configuráveis.
  - `MetadataEnricher`: adiciona metadados como `chunk_id`, `chunk_index`, `char_count`, `is_intro_page`, `section_hint`.

- **Retrieval (`app/retrieval/`)**
  - `RetrievalService`: encapsula embedding de query/documentos e consulta ao `VectorStore`:
    - Gera embedding da pergunta.
    - Consulta ao ChromaDB (`VectorStore.query_nearest`).
    - Filtra candidatos por distância e texto vazio.
    - Deduplicação (_text similarity_) via `_deduplicate_by_similarity`.
    - Rerank heurístico via `rerank` (`RankingService`).
  - `_EmbeddingModel` (`embedding.py`): wrapper de `HuggingFaceEmbeddings` configurado por `settings.embedding_model_name`.
  - `ranking_service.py`: heurísticas de rerank (bônus por termos, padrões de definição, penalidade para títulos/intro/duplicatas).

- **Vector Store (`app/storage/vector_store.py`)**
  - Encapsula `chromadb.PersistentClient` com `collection` configurada por `CHROMA_PATH` e `CHROMA_COLLECTION_NAME`.
  - Interface:
    - `add_vectors(ids, embeddings, documents)` – adiciona vetores + textos + metadados.
    - `query_nearest(query_embedding, k)` – retorna lista de `(page_content, metadata, distance)`.

- **QA / Prompting (`app/qa/`)**
  - `QAService`: serviço de domínio que monta o prompt para o LLM.
  - `prompt_builder.build_prompt`: monta o contexto com tags `[Source: ... | Page: ...]` e injeta instruções em inglês para responder **apenas** com base no contexto.

- **LLM Client (`app/clients/`)**
  - `LLMClient`: gerencia rota de LLMs (`LLM_ROUTE`) e implementa **fallback**:
    - Constrói uma lista de providers (`GeminiProvider`, `OpenAIProvider`) em ordem de prioridade.
    - Para cada provider:
      - Verifica `is_available()` (checa se há API key e client configurado).
      - Chama `generate(prompt)` com timeout configurado.
      - Em caso de erro, faz fallback para o próximo provider.
  - `GeminiProvider`: usa `google.genai.Client` e `generate_content`.
  - `OpenAIProvider`: usa `OpenAI(...).responses.create` com `model` e `input`.

- **Configuração e dependências (`app/core/`)**
  - `config.Settings`: centraliza variáveis de ambiente e defaults.
  - `dependencies.py`: provê singletons para `VectorStore`, `RetrievalService`, `DocumentProcessingService`, `QAService`, `LLMClient` e pipelines.
  - `logging.py` e `log_decorators.py`: configuração e decorators de logging.

- **UI Streamlit (`ui/`)**
  - `ui/streamlit_app.py`: app principal com duas abas:
    - “Upload de documentos”
    - “Chat de perguntas e respostas”
  - `ui/services/api_client.py`: cliente HTTP para a API (`/health`, `/documents`, `/question`).
  - `ui/pages/1_upload.py`: página de upload e indexação de PDFs.
  - `ui/pages/2_chat.py`: página de chat RAG.
  - `ui/components/*`: componentes de UI (sidebar, chat box, referências, chunks).
  - `ui/state/session_state.py`: gerenciamento de estado da sessão (chat, referências, status da API).
  - `ui/config/settings.py`: configurações da UI (API_BASE_URL, timeout).

### Diagrama (Mermaid)

```mermaid
flowchart LR
    subgraph User
        U1[Upload PDF (UI)]
        U2[Pergunta (UI)]
    end

    subgraph UI[Streamlit UI]
        UI_API[ui/services/api_client.py]
    end

    subgraph API[FastAPI]
        DRoute[/POST /documents/]
        QRoute[/POST /question/]
        Health[/GET /health/]
    end

    subgraph Ingestion[IngestionPipeline]
        DPS[DocumentProcessingService\n(loader → preproc → chunking → metadata)]
        RSemb[RetrievalService.embed_documents]
        VSadd[VectorStore.add_vectors]
    end

    subgraph Retrieval[QuestionPipeline]
        RS[RetrievalService.retrieve]
        QA[QAService.build_prompt]
        LLM[LLMClient.generate\n(Gemini/OpenAI + fallback)]
    end

    subgraph Storage[ChromaDB]
        CH[PersistentClient + Collection]
    end

    U1 --> UI
    U2 --> UI

    UI_API -->|upload_document| DRoute
    UI_API -->|ask_question| QRoute
    UI_API -->|health_check| Health

    DRoute --> Ingestion
    Ingestion --> CH

    QRoute --> Retrieval
    Retrieval --> CH
    Retrieval --> QA --> LLM

    LLM --> QRoute --> UI_API --> U2
```

---

## Guia rápido (Quickstart)

> **Se você nunca rodou o projeto antes, siga exatamente esta ordem.**

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPO>
cd ml_rag_challenge
```

### 2. Criar o arquivo `.env` a partir do `.env.example`

O projeto **não funciona** sem algumas variáveis de ambiente mínimas, em especial as chaves das APIs de LLM.

```bash
cp .env.example .env
```

Edite o arquivo `.env` e ajuste pelo menos:

```env
# Caminhos para dados (backend)
CHROMA_PATH=data/chroma
UPLOAD_DIR=data/raw

# Logging
LOG_LEVEL=INFO

# LLM: ordem de fallback (provider:model)
LLM_TIMEOUT_SECONDS=60
LLM_ROUTE=gemini:gemini-3-flash-preview,gemini:gemini-2.5-flash,openai:gpt-4.1-mini

# Chaves de API (obrigatórias para usar LLM)
GEMINI_API_KEY=SEU_TOKEN_GEMINI_AQUI
OPENAI_API_KEY=SEU_TOKEN_OPENAI_AQUI

# UI (Streamlit)
# Para uso local:
API_BASE_URL=http://localhost:8000
UI_HTTP_TIMEOUT_SECONDS=60
```

> Sem `GEMINI_API_KEY` e/ou `OPENAI_API_KEY`, o `LLMClient` não consegue configurar nenhum provider e o pipeline de perguntas irá falhar.

---

## Executando com Docker (recomendado para primeiro uso)

Pré-requisitos:

- Docker instalado
- Docker Compose (ou `docker compose` já disponível na sua versão do Docker)
- Arquivo `.env` configurado (veja seção anterior)

### 1. Build e subida dos serviços

Na raiz do projeto:

```bash
docker compose up --build
```

Isso irá:

- Construir a imagem da **API** a partir de `Dockerfile.api`.
- Construir a imagem da **UI** a partir de `Dockerfile.ui`.
- Criar um volume `rag_data` compartilhado para os dados (`/app/data`) da API.
- Ler o arquivo `.env` e aplicar as variáveis de ambiente para os serviços.

Após a subida:

- API: `http://localhost:8000`
  - Healthcheck: `http://localhost:8000/health`
  - Docs Swagger: `http://localhost:8000/docs`
- UI (Streamlit): `http://localhost:8501`

> No `docker-compose.yml`, a UI é configurada com `API_BASE_URL=http://api:8000`, que é o hostname interno do serviço da API dentro da rede do Docker. Você **não** precisa mudar isso no `.env` para rodar com Compose.

### 2. Parar os serviços

```bash
docker compose down
```

### 3. Remover volumes (apaga índice do Chroma e uploads)

```bash
docker compose down -v
```

> Cuidado: isso apagará definitivamente o índice vetorial e os documentos já ingeridos.

### 4. Ver logs

```bash
docker compose logs -f         # todos os serviços
docker compose logs -f api     # apenas API
docker compose logs -f ui      # apenas UI
```

---

## Executando sem Docker (ambiente local)

Pré-requisitos:

- Python 3.10+
- `pip` atualizado
- Arquivo `.env` configurado

### 1. Criar e ativar ambiente virtual

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Garantir variáveis de ambiente

O mais simples é usar o `.env` já criado. O `pydantic-settings` carrega esse arquivo automaticamente para a API e para a UI.

Se preferir exportar variáveis manualmente (opcional), exemplos:

```bash
export CHROMA_PATH=data/chroma
export UPLOAD_DIR=data/raw
export GEMINI_API_KEY=SEU_TOKEN_GEMINI_AQUI
export OPENAI_API_KEY=SEU_TOKEN_OPENAI_AQUI
export LLM_ROUTE=gemini:gemini-3-flash-preview,gemini:gemini-2.5-flash,openai:gpt-4.1-mini
export API_BASE_URL=http://localhost:8000
```

### 4. Subir a API (FastAPI)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verifique se está tudo ok:

```bash
curl http://localhost:8000/health
```

### 5. Subir a UI (Streamlit)

Em outro terminal, com o mesmo ambiente virtual ativado:

```bash
streamlit run ui/streamlit_app.py
```

Acesse:

- API: `http://localhost:8000`
- UI: `http://localhost:8501`

---

## Como usar a aplicação (passo a passo)

1. **Suba a API e a UI** (via Docker Compose ou localmente, conforme seções anteriores).
2. **Abra a UI no navegador** em `http://localhost:8501`.
3. Na aba **“Upload de documentos”**:
   - Selecione um ou mais arquivos `.pdf`.
   - Clique em **“Indexar PDFs”**.
   - Verifique as mensagens de sucesso/erro para cada arquivo.
4. Após pelo menos um documento ser indexado, vá para a aba **“Chat RAG”**:
   - Digite sua pergunta no campo **“Pergunta”**.
   - Clique em **“Enviar”**.
   - A UI exibirá:
     - a resposta gerada pelo LLM,
     - a lista de referências (documento + página),
     - opcionalmente, os chunks recuperados com scores e trechos de texto.
5. Se algo não funcionar:
   - Verifique a sidebar da UI: ela mostra o status da API (`/health`).
   - Confira se o `.env` está com chaves válidas (`GEMINI_API_KEY`, `OPENAI_API_KEY`).
   - Veja os logs do backend (terminal local ou `docker compose logs api`).

---

## Como usar a API diretamente (sem UI)

### Healthcheck

```bash
curl http://localhost:8000/health
```

### Upload de documento

```bash
curl -X POST "http://localhost:8000/documents" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@seu_documento.pdf;type=application/pdf"
```

Resposta esperada (exemplo):

```json
{
  "message": "Document processed and indexed successfully",
  "documents_indexed": 1,
  "total_chunks": 42
}
```

### Pergunta (RAG)

```bash
curl -X POST "http://localhost:8000/question?top_k=5&initial_k=30" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "O que é um motor elétrico?"
  }'
```

Resposta esperada (estrutura simplificada):

```json
{
  "answer": "Texto da resposta gerada pelo LLM...",
  "references": [
    "documento1.pdf - page 3"
  ],
  "retrieved_chunks": [
    {
      "text": "Trecho completo do chunk...",
      "source": "documento1.pdf",
      "page": 3,
      "distance": 0.123,
      "score": 0.89,
      "rerank_score": 1.23,
      "chunk_index": 10,
      "char_count": 450,
      "is_intro_page": false,
      "section_hint": "Definição de motor elétrico"
    }
  ]
}
```

---

## Dúvidas e troubleshooting

- **Erro de provider LLM / nenhum provider configurado**  
  - Verifique se `GEMINI_API_KEY` e/ou `OPENAI_API_KEY` estão setadas no `.env`.  
  - Confira se `LLM_ROUTE` está no formato `provider:model` e se os providers usados existem.
- **API responde mas a UI diz que está offline**  
  - Confira o valor de `API_BASE_URL` no `.env`:
    - Local sem Docker: `http://localhost:8000`
    - Docker Compose: a variável é sobrescrita para `http://api:8000` no `docker-compose.yml`.
- **Nenhuma resposta relevante / poucas referências**  
  - Certifique-se de que você fez upload de PDFs relacionados ao assunto da pergunta.  
  - Reindexe os documentos se tiver alterado configurações de embedding ou armazenamento.

Com as instruções acima, alguém que nunca usou o projeto deve conseguir:

1. Configurar o `.env` com as chaves de API e paths de dados.  
2. Subir API e UI (com ou sem Docker).  
3. Fazer upload de PDFs e começar a perguntar usando a UI ou a API diretamente.

