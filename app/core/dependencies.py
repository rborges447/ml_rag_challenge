from app.core.config import settings


def get_settings():
    return settings


_vector_store = None


def get_vector_store():
    """VectorStore sem embedding (apenas armazena e consulta vetores). Usado por RetrievalService e IngestionPipeline."""
    global _vector_store
    if _vector_store is None:
        from app.storage.vector_store import VectorStore
        _vector_store = VectorStore()
    return _vector_store


_retrieval_service = None


def get_retrieval_service():
    """Singleton do serviço de retrieval. Usado pelo QuestionPipeline e pelo IngestionPipeline (embed_documents)."""
    global _retrieval_service
    if _retrieval_service is None:
        from app.retrieval import RetrievalService
        _retrieval_service = RetrievalService(vector_store=get_vector_store())
    return _retrieval_service
