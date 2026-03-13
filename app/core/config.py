from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ML Engineering Challenge - RAG API"

    # ========================
    # Vector Store / Embeddings
    # ========================
    openai_api_key: str | None = None
    chroma_path: str = "data/chroma"
    chroma_collection_name: str = "documents"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # ========================
    # Ingestão (paths)
    # ========================
    upload_dir: str = "data/raw"

    # ========================
    # Chunking (ingestão)
    # ========================
    chunk_size: int = 1000
    chunk_overlap: int = 200
    intro_page_max: int = 2

    # ========================
    # Retrieval (duas etapas + rerank)
    # ========================
    retrieval_initial_k: int = 30
    retrieval_top_k_final: int = 5
    retrieval_max_distance: float | None = None
    retrieval_min_score: float | None = None

    # ========================
    # LLM Providers
    # ========================
    llm_providers: str = "gemini"
    llm_timeout_seconds: int = 60

    # Gemini
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    # OpenAI
    openai_model: str = "gpt-4o-mini"

    # OpenRouter
    openrouter_api_key: str | None = None
    openrouter_model: str = "openrouter/auto"

    # Groq
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def llm_provider_list(self) -> list[str]:
        return [p.strip() for p in self.llm_providers.split(",") if p.strip()]


settings = Settings()
