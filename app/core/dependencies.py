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


_document_processing_service = None


def get_document_processing_service():
    """Singleton do serviço de processamento de documentos. Usado pelo IngestionPipeline."""
    global _document_processing_service
    if _document_processing_service is None:
        from app.document_processor import DocumentProcessingService
        _document_processing_service = DocumentProcessingService()
    return _document_processing_service


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


_ingestion_pipeline = None
_question_pipeline = None


def get_ingestion_pipeline():
    """Singleton do IngestionPipeline (documento → vetores)."""
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        from app.pipelines import IngestionPipeline

        _ingestion_pipeline = IngestionPipeline(
            document_processing_service=get_document_processing_service(),
            retrieval_service=get_retrieval_service(),
            vector_store=get_vector_store(),
        )
    return _ingestion_pipeline


def get_question_pipeline():
    """Singleton do QuestionPipeline (pergunta → retrieval + geração)."""
    global _question_pipeline
    if _question_pipeline is None:
        from app.pipelines import QuestionPipeline

        _question_pipeline = QuestionPipeline(
            retrieval_service=get_retrieval_service(),
            qa_service=get_qa_service(),
            llm_client=get_llm_client(),
        )
    return _question_pipeline
