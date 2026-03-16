"""
Pipeline de ingestão: orquestra o DocumentProcessingService (loader → preprocessor → chunking → metadata enricher)
e os serviços externos de embeddings (RetrievalService) e armazenamento (VectorStore).
"""
import uuid

from app.core.dependencies import (
    get_document_processing_service,
    get_retrieval_service,
    get_vector_store,
)
from app.core.log_decorators import log_ingestion_run
from app.document_processor import DocumentProcessingService
from app.retrieval import RetrievalService
from app.storage.vector_store import VectorStore


class IngestionPipeline:
    """
    Orquestra o fluxo completo de ingestão:
    - usa o DocumentProcessingService para transformar o documento em chunks enriquecidos;
    - usa RetrievalService para gerar embeddings das chunks;
    - usa VectorStore para persistir os vetores.

    Mantém o mesmo contrato de retorno exposto para a API.
    """

    def __init__(
        self,
        ingestion_service: DocumentProcessingService | None = None,
        retrieval_service: RetrievalService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self._ingestion_service = ingestion_service or get_document_processing_service()
        self._retrieval_service = retrieval_service or get_retrieval_service()
        self._vector_store = vector_store or get_vector_store()

    @log_ingestion_run
    def run(
        self,
        file_path: str,
        source_name: str,
        request_id: str | None = None,
    ) -> dict:
        """
        Executa o pipeline de ingestão completo.

        Retorna:
        {
            "total_chunks": int,
            "_log": {
                "pages": int,
                "chunks": int,
                "embeddings": int,
                "persisted": int,
            },
        }
        """
        service_result = self._ingestion_service.run(
            file_path=file_path,
            source_name=source_name,
            request_id=request_id,
        )
        chunks = service_result.get("chunks") or []
        service_log = service_result.get("_log") or {}

        pages_count = int(service_log.get("pages", 0))
        chunks_count = len(chunks)

        if not chunks:
            return {
                "total_chunks": 0,
                "_log": {
                    "pages": pages_count,
                    "chunks": 0,
                    "embeddings": 0,
                    "persisted": 0,
                },
            }

        texts = [c.page_content for c in chunks]
        embeddings = self._retrieval_service.embed_documents(texts)
        ids = [str(uuid.uuid4()) for _ in chunks]
        self._vector_store.add_vectors(ids=ids, embeddings=embeddings, documents=chunks)

        return {
            "total_chunks": chunks_count,
            "_log": {
                "pages": pages_count,
                "chunks": chunks_count,
                "embeddings": len(embeddings),
                "persisted": len(ids),
            },
        }
