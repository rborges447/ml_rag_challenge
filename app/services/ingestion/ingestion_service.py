"""
Orquestrador do pipeline de ingestão: salva PDF, loader → preprocessor → chunking → metadata → indexing.
"""
import os
import uuid

from fastapi import UploadFile
from langchain_core.documents import Document

from app.services.ingestion.document_loader_service import DocumentLoaderService
from app.services.ingestion.text_preprocessor import TextPreprocessor
from app.services.ingestion.chunking_service import ChunkingService
from app.services.ingestion.metadata_enricher import MetadataEnricher
from app.services.ingestion.indexing_service import IndexingService


class IngestionService:
    """Orquestra o pipeline completo de ingestão de PDF."""

    def __init__(
        self,
        document_loader: DocumentLoaderService | None = None,
        text_preprocessor: TextPreprocessor | None = None,
        chunking_service: ChunkingService | None = None,
        metadata_enricher: MetadataEnricher | None = None,
        indexing_service: IndexingService | None = None,
    ) -> None:
        self.upload_dir = "data/raw"
        self._loader = document_loader or DocumentLoaderService()
        self._preprocessor = text_preprocessor or TextPreprocessor()
        self._chunking = chunking_service or ChunkingService()
        self._metadata_enricher = metadata_enricher or MetadataEnricher()
        self._indexing = indexing_service or IndexingService()

    async def process_uploaded_file(self, file: UploadFile) -> dict:
        os.makedirs(self.upload_dir, exist_ok=True)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{file_id}.pdf")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        source_name = file.filename or os.path.basename(file_path)
        pages_list = self._loader.load(file_path, source_name)
        pages_list = self._preprocessor.preprocess_pages(pages_list)

        documents_for_split = []
        for p in pages_list:
            page_num = p["page"]
            text = p["text"]
            if not text.strip():
                continue
            documents_for_split.append(
                Document(
                    page_content=text,
                    metadata={"source": source_name, "page": page_num},
                )
            )

        chunks = self._chunking.split(documents_for_split)
        self._metadata_enricher.enrich(chunks)
        self._indexing.index(chunks)

        return {"file_path": file_path, "total_chunks": len(chunks)}
