from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ML Engineering Challenge - RAG API"

    # ========================
    # Logging
    # ========================
    log_level: str = "INFO"

    # ========================
    # Vector Store / Embeddings
    # ========================
    chroma_path: str = "data/chroma"
    chroma_collection_name: str = "documents"
    # Modelo multilíngue por default (EN↔PT). Ao trocar, é necessária re-indexação (re-upload dos PDFs).
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
        "openai:gpt-4.1-mini,"
        "gemini:gemini-2.5-flash,"
        "gemini:gemini-3-flash,"
        
    )

    # Gemini
    gemini_api_key: str | None = None

    # OpenAI
    openai_api_key: str | None = None

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