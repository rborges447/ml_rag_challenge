from app.core.config import settings


def get_settings():
    return settings


_embedding = None


def get_embedding_function():
    """Factory para o modelo de embeddings (singleton). Injetar no VectorStore."""
    global _embedding
    if _embedding is None:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        _embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
    return _embedding


_vector_store = None


def get_vector_store():
    """VectorStore com embedding injetado (singleton)."""
    global _vector_store
    if _vector_store is None:
        from app.services.vector_store import VectorStore
        _vector_store = VectorStore(embedding_function=get_embedding_function())
    return _vector_store