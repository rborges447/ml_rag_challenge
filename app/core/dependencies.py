from app.core.config import settings


def get_settings():
    return settings


_embedding = None


def get_embedding_function():
    """Singleton do modelo de embeddings (para testes legados). Pipelines usam EmbeddingService."""
    global _embedding
    if _embedding is None:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        _embedding = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
    return _embedding


_vector_store = None


def get_vector_store():
    """VectorStore sem embedding (apenas armazena e consulta vetores). Os pipelines usam EmbeddingService."""
    global _vector_store
    if _vector_store is None:
        from app.storage.vector_store import VectorStore
        _vector_store = VectorStore()
    return _vector_store
