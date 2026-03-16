"""
Pipeline de ingestão: orquestra o IngestionService (loader → preprocessor → chunking → metadata enricher → embedding → vector store).
"""
from app.core.dependencies import get_ingestion_service
from app.core.log_decorators import log_ingestion_run
from app.ingestion import IngestionService


class IngestionPipeline:
    """Orquestra o fluxo de ingestão delegando ao IngestionService."""

    def __init__(self, ingestion_service: IngestionService | None = None) -> None:
        self._ingestion_service = ingestion_service or get_ingestion_service()

    @log_ingestion_run
    def run(
        self,
        file_path: str,
        source_name: str,
        request_id: str | None = None,
    ) -> dict:
        """
        Executa o pipeline de ingestão via IngestionService.
        Retorna {"total_chunks": int, "_log": ...}.
        """
        return self._ingestion_service.run(
            file_path=file_path,
            source_name=source_name,
            request_id=request_id,
        )
