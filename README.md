# 📄 RAG API & UI
> Sistema de Perguntas e Respostas sobre Documentos PDF

**FastAPI** • **ChromaDB** • **HuggingFace** • **Gemini / OpenAI** • **Streamlit**

---

## 🤔 O que é este projeto?

Este projeto é um sistema completo de **RAG (Retrieval-Augmented Generation)** — uma técnica de IA que permite fazer perguntas sobre documentos PDF e receber respostas precisas baseadas no conteúdo real dos arquivos.

Em vez de uma IA que "chuta" respostas, este sistema **lê seus documentos, indexa o conteúdo e só então responde** — com referências ao trecho exato de onde a resposta veio.

| | |
|---|---|
| 🧠 **O que faz?** | Responde perguntas sobre documentos PDF com IA |
| ⚙️ **Back-end** | FastAPI + ChromaDB + HuggingFace Embeddings |
| 🖥️ **Interface** | Streamlit — simples e visual |
| 🤖 **IA** | Google Gemini ou OpenAI (com fallback automático) |
| 🐳 **Deploy** | Docker Compose — sobe tudo com um comando |

---

## 🚀 Início Rápido (3 minutos)

### Pré-requisitos
- Docker instalado na máquina
- Chave de API do **Google Gemini** ou **OpenAI** (pelo menos uma)

### Passo 1 — Clone o repositório
```bash
git clone <REPO_URL>
cd ml_rag_challenge
```

### Passo 2 — Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Abra o arquivo `.env` e adicione pelo menos uma chave de API:
```env
GEMINI_API_KEY=sua_chave_aqui
OPENAI_API_KEY=sua_chave_aqui
```

> 💡 **Dica:** Apenas uma chave é obrigatória. Se configurar as duas, o sistema usa fallback automático entre provedores.

### Passo 3 — Suba os serviços
```bash
# Primeira vez (ou após mudar requirements.txt / imagem base)
docker compose up --build

# Uso diário (mais rápido, reaproveita a imagem já construída)
docker compose up -d
```

Aguarde o build terminar. Na primeira vez pode levar alguns minutos (especialmente ao instalar dependências).

### Serviços disponíveis

| Serviço | URL | Descrição |
|---|---|---|
| **API** | http://localhost:8000 | Back-end principal |
| **Swagger Docs** | http://localhost:8000/docs | Documentação interativa da API |
| **Interface Web** | http://localhost:8501 | UI para upload e perguntas |

---

## 📖 Como usar

### Pela interface web (Streamlit)

1. Acesse **http://localhost:8501** no seu navegador
2. Faça upload de um ou mais documentos PDF
3. Vá para a página de **Chat**
4. Faça sua pergunta e receba a resposta com referências ao documento

### Pela API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Verifica se a API está rodando |
| `POST` | `/documents` | Faz upload de um PDF |
| `POST` | `/question` | Faz uma pergunta |
```bash
# Health check
curl http://localhost:8000/health

# Upload de documento
curl -X POST http://localhost:8000/documents \
  -F "file=@documento.pdf"

# Fazer uma pergunta
curl -X POST http://localhost:8000/question \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é um motor de indução?"}'
```

---

## 💡 Exemplos de perguntas e respostas

Os PDFs de exemplo estão na pasta `example_data/`. Faça upload e teste:

**LB5001.pdf**
> ❓ How often should motor bearings be lubricated for motors up to frame size 210 at 1800 RPM?
> ✅ Motor bearings should be relubricated every 12,000 hours.

**MN414_0224.pdf**
> ❓ What lubricant is recommended for new Baldor submersible motors?
> ✅ Shell Rotella SAE 10W. New motors ship with the oil reservoir properly filled.

**WEG-CESTARI manual**
> ❓ Within what maximum period must WEG-CESTARI gear units be put into operation after leaving the factory?
> ✅ Within a maximum period of 6 months after leaving the factory.

**WEG motor (em português)**
> ❓ Por que o motor de indução é o tipo de motor elétrico mais utilizado?
> ✅ Construção simples, alta confiabilidade, baixo custo, baixa manutenção e boa eficiência.

> **Nota:** O texto exato da resposta pode variar conforme o provedor de IA, mas as informações-chave devem coincidir.

**Rodar exemplos de perguntas via Docker (scripts/exemples_questions.py)**
```bash
# Compor e rodar diretamente um container novo
docker compose run --rm api python scripts/exemples_questions.py

# Ou, se a stack já estiver subida com `docker compose up`
docker compose exec api python scripts/exemples_questions.py

---

## 🏗️ Como o sistema funciona

O sistema opera em dois pipelines:

**Ingestão (upload de PDF)**
```
PDF → extração de texto → limpeza → chunking → embeddings → ChromaDB
```

**Perguntas**
```
pergunta → embedding → busca vetorial → reranking → prompt → LLM → resposta
```

---

## ⚙️ Diferenciais técnicos

**Query Expansion (EN → PT)**
Termos técnicos em inglês são expandidos para equivalentes em português, melhorando a recuperação quando a pergunta está em inglês mas o documento está em português.

**Reranking Heurístico**
Perguntas conceituais ("por que", "vantagens", "how does it work") tendem a estar em seções introdutórias. O reranker detecta esse padrão e ajusta a pontuação dos chunks.

**Deduplicação de Chunks**
Chunks muito similares são removidos antes de serem enviados ao LLM, evitando contexto redundante.

**Fallback entre provedores de LLM**
Se o provedor primário falhar, o sistema tenta automaticamente o segundo provedor — sem interrupção para o usuário.

```


```

---

## 📁 Estrutura do projeto
```
app/
├── api/                # Rotas FastAPI
├── pipelines/          # Ingestão e perguntas
├── retrieval/          # Busca e reranking
├── document_processor/ # Processamento de PDF
├── storage/            # Abstração do banco vetorial
├── qa/                 # Construção de prompts
├── clients/            # Provedores de LLM
└── core/               # Config, logging, dependências

ui/
├── pages/              # Páginas da interface
├── components/         # Componentes reutilizáveis
└── services/           # Comunicação com a API

scripts/
└── exemple_questions.py
```

---

## 🛠️ Rodando sem Docker (opcional)
```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux / Mac
.venv\Scripts\activate         # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Iniciar a API
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Iniciar a interface (em outro terminal)
streamlit run ui/streamlit_app.py
```

---

## 🔧 Resolução de problemas

**Nenhum provedor de IA disponível**
Verifique se o `.env` contém pelo menos uma chave:
```env
GEMINI_API_KEY=sua_chave
# ou
OPENAI_API_KEY=sua_chave
```

**Qualidade de recuperação ruim**
- Documentos não foram indexados — faça upload novamente
- O modelo de embedding foi alterado — reindexe os documentos
- Documentos sem relação com a pergunta — verifique os arquivos enviados

**Serviços não sobem com Docker**
```bash
docker ps                          # verifica se o Docker está rodando
docker compose logs api ui         # inspeciona os logs de cada serviço
```
> 💡 Use `docker compose up --build` apenas quando alterar dependências (por exemplo, `requirements.txt`) ou a imagem base. No dia a dia, prefira `docker compose up -d`, que é muito mais rápido por reaproveitar as imagens já construídas.
> Confirme também que as portas `8000` e `8501` não estão em uso.

---

*Construído com foco em qualidade de retrieval, arquitetura modular e experiência de desenvolvimento.*