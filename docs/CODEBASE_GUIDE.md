# Guia do codebase – RAG API (para IA e desenvolvedores)

Este documento descreve o funcionamento do projeto para que uma IA ou um desenvolvedor entenda a arquitetura, os fluxos e o papel de cada arquivo **sem precisar ler todo o código**.

---

## 1. Visão geral

- **O que é:** API REST em FastAPI para um pipeline RAG (Retrieval-Augmented Generation) **sem geração por LLM**. Hoje o sistema apenas **indexa PDFs** e **recupera chunks relevantes** para uma pergunta.
- **Stack:** FastAPI, LangChain (como biblioteca interna), ChromaDB (vetorial persistente), HuggingFace (embeddings).
- **Arquitetura:** Camadas bem definidas: **API (rotas)** → **services (lógica)** → **core (config e dependências)**. Nenhuma rota contém lógica pesada; os services orquestram ingestão e retrieval.
- **Fluxos principais:**
  1. **Ingestão:** upload de PDF → salvar em disco → extrair texto (PyMuPDF) → pré-processar → chunking → metadados ricos → embeddings e persistência no Chroma.
  2. **Retrieval:** pergunta → busca vetorial (muitos candidatos) → deduplicação por similaridade → reranking heurístico → retorno dos top-K chunks com scores.

---

## 2. Estrutura de pastas e responsabilidades

```
app/
├── main.py                    # Ponto de entrada FastAPI; registra rotas e /health
├── api/
│   ├── routes_documents.py   # POST /documents (upload de PDF)
│   └── routes_questions.py   # POST /question (pergunta → chunks)
├── core/
│   ├── config.py             # Settings (Pydantic): paths, chunk, retrieval, embedding
│   └── dependencies.py       # Singletons: get_embedding_function(), get_vector_store()
├── schemas/
│   ├── document.py           # DocumentUploadResponse (Pydantic)
│   └── question.py           # QuestionRequest, QuestionResponse (Pydantic)
├── services/
│   ├── document_ingestion_service.py  # Orquestra: PDF → pré-processo → chunk → Chroma
│   ├── pdf_text_utils.py             # Pré-processamento puro (normalização, ruído, headers/footers)
│   ├── vector_store.py               # Encapsula Chroma (LangChain); add_documents, similarity_search_with_score
│   ├── reranker.py                   # Reranking heurístico (bônus/penalidades, score explicável)
│   ├── retrieval_service.py          # Duas etapas: busca ampla + rerank; dedup por similaridade
│   └── qa_service.py                 # Fachada: hoje só delega retrieval; futuro: retrieval + LLM
├── clients/
│   └── llm_client.py          # Stub para futuro cliente LLM
scripts/
└── benchmark_retrieval.py     # Benchmark top-1/top-3/top-5 com perguntas fixas
data/
├── raw/                      # PDFs enviados (upload)
└── chroma/                  # Persistência do ChromaDB (coleção de vetores)
```

- **API:** só valida entrada, chama service e devolve resposta.
- **Services:** contêm toda a lógica; usam LangChain e Chroma internamente, mas a interface exposta é do projeto (não “caixa-preta” LangChain).
- **Core:** config centralizada e factories (embedding, vector store) para injeção e reuso.

---

## 3. Configuração (app/core/config.py)

Classe `Settings` (Pydantic BaseSettings). Valores podem vir de `.env` ou variáveis de ambiente (nomes em UPPER).

| Variável | Tipo | Default | Uso |
|----------|------|---------|-----|
| `chroma_path` | str | "data/chroma" | Diretório de persistência do Chroma |
| `chroma_collection_name` | str | "documents" | Nome da coleção no Chroma |
| `embedding_model_name` | str | "all-MiniLM-L6-v2" | Modelo HuggingFace para embeddings |
| `chunk_size` | int | 1000 | Tamanho alvo do chunk (caracteres) |
| `chunk_overlap` | int | 200 | Overlap entre chunks |
| `intro_page_max` | int | 2 | Páginas ≤ este número são consideradas introdutórias (heurística) |
| `retrieval_initial_k` | int | 30 | Quantos candidatos buscar no Chroma antes do rerank |
| `retrieval_top_k_final` | int | 5 | Quantos chunks retornar após rerank |
| `retrieval_max_distance` | float \| None | None | Filtrar por distância L2 máxima (Chroma) |
| `retrieval_min_score` | float \| None | None | Score mínimo pós-rerank para incluir chunk |

---

## 4. Dependências (app/core/dependencies.py)

- **get_settings()** – retorna `settings` (config).
- **get_embedding_function()** – singleton de `HuggingFaceEmbeddings` (LangChain). Usado para injetar no VectorStore; evita criar o modelo em todo lugar.
- **get_vector_store()** – singleton de `VectorStore` já com `embedding_function=get_embedding_function()`. Ingestão e retrieval usam o mesmo store.

Assim, o VectorStore não “possui” o modelo de embedding; ele recebe a função por injeção (ou usa default interno se não for passada).

---

## 5. Fluxo de ingestão (POST /documents)

1. **Rota** (`routes_documents.py`): valida que o arquivo é PDF; chama `document_ingestion_service.process_uploaded_file(file)`; retorna `DocumentUploadResponse` com `total_chunks`.
2. **DocumentIngestionService.process_uploaded_file**:
   - Cria `data/raw` se não existir; gera UUID e salva o PDF em `data/raw/{uuid}.pdf`.
   - Usa **PyMuPDFLoader** (LangChain) para carregar o PDF → lista de `Document` (um por página), com `page_content` e `metadata` (ex.: `page` 0-based).
   - Converte para lista de dicts `{"page": page_num_1_indexed, "text": page_content}`.
   - Chama **preprocess_pages** (pdf_text_utils): ver seção 6.
   - Reconstrói `Document` por página (só páginas com texto); metadados iniciais: `source` (nome do arquivo), `page`.
   - Aplica **RecursiveCharacterTextSplitter** (LangChain) com `chunk_size` e `chunk_overlap` da config; separadores: `["\n\n", "\n", ". ", " ", ""]`.
   - Para cada chunk, enriquece metadados: `chunk_id` (UUID), `chunk_index` (índice global), `char_count`, `is_intro_page` (heurística: página ≤ intro_page_max ou marcadores de introdução + pouco texto), `section_hint` (primeira linha curta do chunk, se parecer título).
   - Chama **vector_store.add_documents(chunks)** → Chroma gera embeddings e persiste (ids internos UUID).
3. **Resposta:** `{ "message": "...", "documents_indexed": 1, "total_chunks": N }`.

---

## 6. Pré-processamento (app/services/pdf_text_utils.py)

Funções **puras** (sem I/O, sem estado global). Entrada/saída em texto ou lista de páginas.

- **normalize_text(text):** unifica quebras de linha (`\r\n`, `\r` → `\n`), colapsa múltiplos espaços por linha, remove `\x00` e `\t`, colapsa `\n{3,}` em `\n\n`.
- **remove_noise_lines(lines, ...):** remove linhas muito curtas, só números (ex.: número de página), só pontuação/espaços.
- **remove_repeated_headers_footers(pages, threshold=0.5):** para cada linha “normalizada” (fingerprint até 80 chars), conta em quantas páginas aparece; remove linhas que aparecem em ≥ threshold das páginas (ex.: 50%) – típico de cabeçalho/rodapé.
- **remove_generic_only_blocks(text):** remove blocos (parágrafos) que são uma única linha e contêm apenas frases genéricas (ex.: "Sumário", "Introdução", "Página X") – conjunto `GENERIC_PHRASES`.
- **preprocess_pages(pages):** pipeline: para cada página aplica normalize → remove_noise_lines → remove_generic_only_blocks; depois remove_repeated_headers_footers. Entrada/saída: `list[{"page": int, "text": str}]`.

---

## 7. Vector store (app/services/vector_store.py)

- **Propósito:** abstrair o Chroma (via LangChain). Interface do projeto: não expõe Chroma nem LangChain para as rotas.
- **Construtor:** `embedding_function` opcional (tipo Embeddings). Se `None`, usa `HuggingFaceEmbeddings(settings.embedding_model_name)`. Também aceita `persist_directory` e `collection_name` (defaults em config).
- **add_documents(documents: list[Document]) -> list[str]:** gera um UUID por documento, chama `_store.add_documents(documents, ids=ids)`. Chroma usa o `embedding_function` para embedar e persiste. Retorna os ids.
- **similarity_search_with_score(query, k):** retorna `list[tuple[Document, float]]`. O float é **distância L2** (menor = mais similar).
- **get_retriever(k, **kwargs):** retorna retriever LangChain (similarity) para uso externo se necessário.

Document é do LangChain: `page_content: str`, `metadata: dict`.

---

## 8. Reranking heurístico (app/services/reranker.py)

- **Entrada:** `query: str`, `candidates: list[tuple[Document, float]]` (documento + distância L2).
- **Saída:** `list[tuple[Document, float, float]]` – mesmo documento e distância, mais um **rerank_score** (maior = melhor). Ordenado por rerank_score decrescente.

**Cálculo do rerank_score (explicável):**

- **Base:** score vetorial = `1 / (1 + distance)`.
- **Bônus:**  
  - Termos da pergunta no chunk: tokenização simples (palavras 2+ chars, normalizadas sem acento); +0.08 por termo presente, teto 0.35.  
  - Pergunta definicional (“o que é X”) e chunk com padrão de definição (“X é”, “X são”, “define-se”, etc.): +0.25.  
  - Frase exata da pergunta (normalizada) contida no chunk: +0.2.
- **Penalizações:**  
  - Chunk com `char_count` < 100: -0.12.  
  - Chunk que parece só título (uma linha curta ou começa com “número.”): -0.1.  
  - Metadado `is_intro_page` True: -0.15.  
  - Par de chunks com similaridade de texto ≥ 0.88: o de menor rerank_score recebe -0.2.

Constantes (BONUS_*, PENALTY_*, etc.) estão no topo do arquivo para ajuste fino.

---

## 9. Retrieval em duas etapas (app/services/retrieval_service.py)

- **RetrievalService** usa `get_vector_store()` (singleton).
- **retrieve(question, top_k=None, initial_k=None, max_distance=None, min_score=None):**
  1. **Busca:** `similarity_search_with_score(question, k=initial_k)` (default da config: 30).
  2. **Filtro:** descarta candidatos com `distance > max_distance` (se configurado) e chunks com texto vazio.
  3. **Deduplicação:** `_deduplicate_by_similarity(candidates, threshold=0.9)` – mantém um por “grupo” de textos muito parecidos (SequenceMatcher), preservando o de menor distância.
  4. **Rerank:** `rerank(question, candidates)` → lista ordenada por rerank_score.
  5. **Saída:** para cada item, filtra por `min_score` (se configurado), corta em `top_k` (default config: 5), e monta dict por chunk com: `text`, `source`, `page`, `distance`, `score` (vetorial 1/(1+distance)), `rerank_score`, e metadados: `chunk_index`, `char_count`, `is_intro_page`, `section_hint`.

---

## 10. QA service (app/services/qa_service.py)

- **Papel:** fachada para “pergunta → resposta”. Hoje só há retrieval; no futuro aqui entraria retrieval + chamada a LLM.
- **get_qa_service()** retorna uma instância de **QAService**.
- **QAService.retrieve(...)** repassa todos os parâmetros para **RetrievalService.retrieve(...)**. A rota de perguntas chama `qa_service.retrieve()` para que, no futuro, a troca para “retrieval + LLM” seja feita só neste serviço.

---

## 11. Fluxo de perguntas (POST /question)

1. **Rota** (`routes_questions.py`): body `QuestionRequest` com `question: str`; query params opcionais: `top_k` (default 5), `initial_k`, `max_distance`. Chama `qa_service.retrieve(question, top_k=..., initial_k=..., max_distance=...)`.
2. **Resposta:** `{ "question": "...", "retrieved_chunks": [ {...}, ... ] }`. Cada elemento de `retrieved_chunks` contém os campos descritos na seção 9 (text, source, page, distance, score, rerank_score, metadados).

---

## 12. Schemas (request/response)

- **document.py:** `DocumentUploadResponse`: `message`, `documents_indexed`, `total_chunks`.
- **question.py:** `QuestionRequest`: `question` (str, min_length=1). `QuestionResponse` existe (answer, references) mas **não é usada** na rota atual; a rota retorna dict com `question` e `retrieved_chunks`.

---

## 13. Benchmark (scripts/benchmark_retrieval.py)

- **Objetivo:** avaliar se o chunk “relevante” aparece no top-1, top-3 e top-5 para um conjunto fixo de perguntas (ex.: sobre motores elétricos).
- **Pré-requisito:** Chroma já indexado (pelo menos um PDF via POST /documents).
- **Execução:** na raiz do projeto, `python scripts/benchmark_retrieval.py`. O script adiciona a raiz ao `sys.path` e importa `RetrievalService`.
- **Lógica:** para cada pergunta em `BENCHMARK_QUESTIONS` (pergunta + lista de `required_terms`), chama `service.retrieve(question, top_k=5)`. Considera “acerto” em top-K se **algum** chunk no top-K contiver **todos** os termos de `required_terms` (case-insensitive).
- **Saída:** por pergunta, indica top-1 ok, top-3 ok, top-5 ok e número de chunks; no final, resumo contando quantas perguntas acertaram em top-1, top-3 e top-5.

---

## 14. Dependências entre módulos (quem chama quem)

- **main** → api (rotas).
- **routes_documents** → schemas.document, DocumentIngestionService.
- **routes_questions** → schemas.question, qa_service.
- **DocumentIngestionService** → config, dependencies (get_vector_store), pdf_text_utils (preprocess_pages), vector_store (VectorStore tipo), LangChain (PyMuPDFLoader, RecursiveCharacterTextSplitter, Document).
- **RetrievalService** → config, dependencies (get_vector_store), reranker (rerank).
- **QAService** → RetrievalService.
- **VectorStore** → config, LangChain (Chroma, HuggingFaceEmbeddings ou embedding injetado).
- **dependencies** → config, HuggingFaceEmbeddings, VectorStore.
- **reranker** → LangChain Document; não depende de outros services do app.
- **pdf_text_utils** → nenhum outro módulo do app (funções puras).

Nenhuma rota importa LangChain nem Chroma diretamente; apenas os services usam essas bibliotecas.

---

## 15. Dados persistidos

- **data/raw:** arquivos PDF enviados (nome `{uuid}.pdf`). Não são apagados automaticamente; a reindexação reutiliza o mesmo arquivo se você mantiver o path.
- **data/chroma:** banco Chroma (SQLite + arquivos de vetores). Cada documento indexado vira um vetor + metadados (source, page, chunk_id, chunk_index, char_count, is_intro_page, section_hint). Para “reindexar” após mudar chunking ou pré-processamento, é necessário **apagar** este diretório e enviar de novo os PDFs via POST /documents.

---

## 16. Resumo para uma IA

- O projeto é uma **API RAG só de retrieval** (sem LLM): indexa PDFs em um vector store e responde perguntas com uma lista de chunks ranqueados.
- **Ingestão:** PDF → salvar → PyMuPDF → pré-processamento (pdf_text_utils) → RecursiveCharacterTextSplitter → metadados ricos → VectorStore.add_documents (Chroma com embeddings HuggingFace).
- **Retrieval:** pergunta → VectorStore.similarity_search_with_score(initial_k) → filtro por distância → deduplicação por similaridade de texto → reranker heurístico (bônus termos/definição/frase exata; penalidades curto/título/intro/duplicados) → top_k_final com rerank_score e metadados.
- **Config** centraliza tamanho de chunk, k inicial/final, thresholds; **dependencies** centralizam embedding e vector store (singleton).
- **Rota /question** retorna apenas `question` e `retrieved_chunks` (sem resposta em linguagem natural). O **qa_service** existe como fachada para futura adição de LLM no mesmo ponto.

Usando este guia, uma IA pode entender o fluxo, onde está cada responsabilidade e como os arquivos se conectam, sem precisar inferir tudo a partir do código fonte.
