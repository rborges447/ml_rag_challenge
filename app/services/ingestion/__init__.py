"""
Pipeline de ingestão: loader, pré-processamento, chunking, metadados.
"""
from app.services.ingestion.chunking_service import ChunkingService
from app.services.ingestion.document_loader_service import DocumentLoaderService
from app.services.ingestion.metadata_enricher import MetadataEnricher
from app.services.ingestion.text_preprocessor import TextPreprocessor

__all__ = [
    "DocumentLoaderService",
    "TextPreprocessor",
    "ChunkingService",
    "MetadataEnricher",
]
