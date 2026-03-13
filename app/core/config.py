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
    # LLM
    # ========================
    llm_timeout_seconds: int = 60
    llm_route: str = (
        "gemini:gemini-3-flash,"
        "gemini:gemini-2.5-flash,"
        "openai:gpt-4.1-mini"
    )

    # Gemini
    gemini_api_key: str | None = None

    # OpenAI
    openai_api_key: str | None = None

    # Mantidos para uso futuro, se quiser
    openrouter_api_key: str | None = None
    openrouter_model: str = "openrouter/auto"

    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def llm_route_list(self) -> list[tuple[str, str]]:
        items: list[tuple[str, str]] = []

        for raw_item in self.llm_route.split(","):
            item = raw_item.strip()
            if not item:
                continue

            if ":" not in item:
                raise ValueError(
                    f"Invalid llm_route item '{item}'. Expected provider:model"
                )

            provider, model = item.split(":", 1)
            items.append((provider.strip().lower(), model.strip()))

        if not items:
            raise ValueError("llm_route cannot be empty")

        return items


settings = Settings()