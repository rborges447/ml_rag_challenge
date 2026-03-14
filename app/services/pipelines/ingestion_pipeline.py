"""
Pipeline 1 — Ingestão: loader → preprocessor → chunking → metadata enricher → embedding → vector store.
"""
import uuid

from langchain_core.documents import Document

from app.core.dependencies import get_vector_store
from app.services.embeddings import EmbeddingService
from app.services.ingestion.chunking_service import ChunkingService
from app.services.ingestion.document_loader_service import DocumentLoaderService
from app.services.ingestion.metadata_enricher import MetadataEnricher
from app.services.ingestion.text_preprocessor import TextPreprocessor


class IngestionPipeline:
    """Orquestra o fluxo de ingestão: documento → chunks enriquecidos → embeddings → vector store."""

    def __init__(
        self,
        document_loader: DocumentLoaderService | None = None,
        text_preprocessor: TextPreprocessor | None = None,
        chunking_service: ChunkingService | None = None,
        metadata_enricher: MetadataEnricher | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store=None,
    ) -> None:
        self._loader = document_loader or DocumentLoaderService()
        self._preprocessor = text_preprocessor or TextPreprocessor()
        self._chunking = chunking_service or ChunkingService()
        self._metadata_enricher = metadata_enricher or MetadataEnricher()
        self._embedding_service = embedding_service or EmbeddingService()
        self._vector_store = vector_store or get_vector_store()

    def run(self, file_path: str, source_name: str) -> dict:
        """
        Executa o pipeline: carrega PDF, preprocessa, chunking, enriquece metadados,
        calcula embeddings e armazena no vector store.
        Retorna {"total_chunks": int}.
        """
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

        if not chunks:
            return {"total_chunks": 0}

        texts = [c.page_content for c in chunks]
        embeddings = self._embedding_service.embed_documents(texts)
        ids = [str(uuid.uuid4()) for _ in chunks]
        self._vector_store.add_vectors(ids=ids, embeddings=embeddings, documents=chunks)

        return {"total_chunks": len(chunks)}
