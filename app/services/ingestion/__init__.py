"""
Pipeline de ingestão: loader, pré-processamento, chunking, metadados, indexação.
"""
from app.services.ingestion.ingestion_service import IngestionService

__all__ = ["IngestionService"]
