# Artefatos da refatoração arquitetural RAG

## 1. Resumo das mudanças

- **Use cases explícitos:** `DocumentIngestionUseCase` (upload → salvar → pipeline de ingestão) e `AnswerQuestionUseCase` (retrieval → generation → resposta com referências). As rotas da API passam a chamar esses use cases diretamente.
- **Três pipelines explícitos:**
  - **IngestionPipeline:** loader → preprocessor → chunking → metadata enricher → EmbeddingService.embed_documents → VectorStore.add_vectors.
  - **RetrievalPipeline:** EmbeddingService.embed_query → VectorStore.similarity_search_with_score_by_vector → dedup → rerank (via RetrievalService).
  - **GenerationPipeline:** build_prompt(question, chunks) → LLMClient.generate → resposta.
- **EmbeddingService:** única camada que calcula embeddings (`embed_documents`, `embed_query`), usada no pipeline de ingestão (após metadata enricher) e no pipeline de retrieval (embed da pergunta).
- **Vector store:** passou a ter apenas armazenamento e consulta de vetores: sem `embedding_function` no construtor; novos métodos `add_vectors(ids, embeddings, documents)` e `similarity_search_with_score_by_vector(query_embedding, k)`. Implementação usando chromadb (PersistentClient) diretamente.
- **RetrievalService:** passou a usar EmbeddingService para embed da pergunta e VectorStore.similarity_search_with_score_by_vector para busca (em vez de similarity_search_with_score com texto).
- **IngestionService e QAService:** mantidos como fachadas que delegam ao use case/pipeline, para compatibilidade com código e testes que ainda os utilizam.
- **dependencies.py:** `get_vector_store()` instancia VectorStore sem embedding; `get_retrieval_service()` para retrieval (embedding é lógica interna do RetrievalService).

---

## 2. Lista de arquivos criados

| Arquivo |
|---------|
| `app/use_cases/__init__.py` |
| `app/use_cases/ingest_document.py` |
| `app/use_cases/answer_question.py` |
| `app/services/pipelines/__init__.py` |
| `app/services/pipelines/ingestion_pipeline.py` |
| `app/services/pipelines/retrieval_pipeline.py` |
| `app/services/pipelines/generation_pipeline.py` |
| `app/services/embeddings/__init__.py` |
| `app/services/embeddings/embedding_service.py` |

---

## 3. Lista de arquivos modificados

| Arquivo | Alteração |
|---------|-----------|
| `app/api/routes_documents.py` | Passa a usar `DocumentIngestionUseCase` em vez de `IngestionService`. |
| `app/api/routes_questions.py` | Passa a usar `AnswerQuestionUseCase` em vez de `get_qa_service()`. |
| `app/core/dependencies.py` | `get_vector_store()` instancia VectorStore sem embedding; `get_retrieval_service()` para retrieval. |
| `app/services/vector_store.py` | Refatorado: só armazena/consulta vetores; `add_vectors` e `similarity_search_with_score_by_vector`; uso de chromadb.PersistentClient. |
| `app/services/ingestion/ingestion_service.py` | Virou fachada: delega a `DocumentIngestionUseCase` (salvar + pipeline). |
| `app/services/retrieval/retrieval_service.py` | Usa `EmbeddingService.embed_query` e `VectorStore.similarity_search_with_score_by_vector`. |
| `app/services/qa/qa_service.py` | Delega `answer()` a `AnswerQuestionUseCase`; import de use case em `__init__` para evitar ciclo. |
| `app/services/__init__.py` | Exporta também `EmbeddingService`, `IngestionPipeline`, `RetrievalPipeline`, `GenerationPipeline`. |
| `tests/test_vector_store.py` | Atualizado para `add_vectors` e `similarity_search_with_score_by_vector` com `FakeEmbeddingService`. |

---

## 4. Explicação da nova arquitetura

- **API (FastAPI):** rotas apenas validam request, chamam o use case e devolvem resposta (sem lógica de negócio).
- **Use cases:** orquestração de alto nível. `DocumentIngestionUseCase` salva o PDF e chama o `IngestionPipeline`. `AnswerQuestionUseCase` chama `RetrievalPipeline` e em seguida `GenerationPipeline`, e monta `references` a partir dos chunks.
- **Pipelines:** fluxo RAG explícito no código. Ingestion: loader → preprocess → chunking → metadata → **embed (EmbeddingService)** → **store (VectorStore.add_vectors)**. Retrieval: **embed query (EmbeddingService)** → **vector search (VectorStore.similarity_search_with_score_by_vector)** → dedup → rerank. Generation: prompt builder → LLMClient (fallback de providers).
- **Serviços:** loader, preprocessor, chunking, metadata enricher, retrieval (busca + rerank), prompt builder. **EmbeddingService** é o único que calcula embeddings. **VectorStore** só persiste e consulta vetores.
- **Clients:** apenas o GenerationPipeline chama o `LLMClient`; fallback de providers (Gemini, OpenAI) permanece inalterado.

Fluxo resumido: **Usuário → UI → API → Use Case → Pipeline(s) → Serviços / VectorStore / LLMClient.**

---

## 5. Confirmação de que nenhum endpoint mudou

| Método | Path | Query params | Body / Response |
|--------|------|--------------|------------------|
| GET | `/health` | — | Response: `{"status": "ok"}` (inalterado) |
| POST | `/documents` | — | Body: multipart PDF (`file`). Response: `DocumentUploadResponse` (message, documents_indexed, total_chunks) — **inalterado** |
| POST | `/question` | `top_k`, `initial_k`, `max_distance` (opcionais) | Body: `QuestionRequest` (question). Response: `QuestionResponse` (answer, references, retrieved_chunks) — **inalterado** |

Nenhum path, método, query parameter ou contrato de request/response foi alterado. A UI Streamlit e clientes HTTP continuam compatíveis.
