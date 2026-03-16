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


_ingestion_service = None


def get_ingestion_service():
    """Singleton do serviço de ingestão. Usado pelo IngestionPipeline."""
    global _ingestion_service
    if _ingestion_service is None:
        from app.ingestion import IngestionService
        _ingestion_service = IngestionService(
            retrieval_service=get_retrieval_service(),
            vector_store=get_vector_store(),
        )
    return _ingestion_service


_qa_service = None


def get_qa_service():
    """Singleton do serviço de QA (montagem de prompt). Usado pelo QuestionPipeline."""
    global _qa_service
    if _qa_service is None:
        from app.qa import QAService
        _qa_service = QAService()
    return _qa_service


_llm_client = None


def get_llm_client():
    """Singleton do cliente LLM. Usado pelo QuestionPipeline."""
    global _llm_client
    if _llm_client is None:
        from app.clients import LLMClient
        _llm_client = LLMClient()
    return _llm_client
