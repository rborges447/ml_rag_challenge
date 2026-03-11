from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ML Engineering Challenge - RAG API"
    openai_api_key: str | None = None
    chroma_path: str = "data/chroma"
    chroma_collection_name: str = "documents"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Chunking (ingestão)
    chunk_size: int = 1000
    chunk_overlap: int = 200
    intro_page_max: int = 2

    # Retrieval (duas etapas + rerank)
    retrieval_initial_k: int = 30
    retrieval_top_k_final: int = 5
    retrieval_max_distance: float | None = None
    retrieval_min_score: float | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()