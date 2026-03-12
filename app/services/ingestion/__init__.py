"""
Pipeline de ingestão: loader, pré-processamento, chunking, metadados, indexação.
"""
from app.services.ingestion.document_loader_service import DocumentLoaderService
from app.services.ingestion.text_preprocessor import TextPreprocessor
from app.services.ingestion.chunking_service import ChunkingService
from app.services.ingestion.metadata_enricher import MetadataEnricher
from app.services.ingestion.indexing_service import IndexingService
from app.services.ingestion.ingestion_service import IngestionService

__all__ = [
    "IngestionService",
    "DocumentLoaderService",
    "TextPreprocessor",
    "ChunkingService",
    "MetadataEnricher",
    "IndexingService",
]
