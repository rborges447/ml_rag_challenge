from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ML Engineering Challenge - RAG API"
    openai_api_key: str | None = None
    chroma_path: str = "data/chroma"
    chroma_collection_name: str = "documents"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()