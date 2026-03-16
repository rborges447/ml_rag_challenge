"""
Serviço de ingestão: fluxo completo loader → preprocessor → chunking → metadata enricher → embed (RetrievalService) → vector store.
"""
import uuid

from langchain_core.documents import Document

from app.ingestion.chunking_service import ChunkingService
from app.ingestion.document_loader_service import DocumentLoaderService
from app.ingestion.metadata_enricher import MetadataEnricher
from app.ingestion.text_preprocessor import TextPreprocessor


class IngestionService:
    """
    Responsável pelo fluxo completo de ingestão: carregar documento, preprocessar,
    fazer chunking, enriquecer metadados, gerar embeddings (via RetrievalService) e persistir no VectorStore.
    """

    def __init__(self, retrieval_service=None, vector_store=None) -> None:
        self._loader = DocumentLoaderService()
        self._preprocessor = TextPreprocessor()
        self._chunking = ChunkingService()
        self._metadata_enricher = MetadataEnricher()
        if retrieval_service is not None:
            self._retrieval_service = retrieval_service
        else:
            from app.core.dependencies import get_retrieval_service
            self._retrieval_service = get_retrieval_service()
        if vector_store is not None:
            self._vector_store = vector_store
        else:
            from app.core.dependencies import get_vector_store
            self._vector_store = get_vector_store()

    def run(
        self,
        file_path: str,
        source_name: str,
        request_id: str | None = None,
    ) -> dict:
        """
        Executa o fluxo de ingestão: carrega PDF, preprocessa, chunking, enriquece metadados,
        calcula embeddings e armazena no vector store.
        Retorna {"total_chunks": int, "_log": ...}.
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
        embeddings = self._retrieval_service.embed_documents(texts)
        ids = [str(uuid.uuid4()) for _ in chunks]
        self._vector_store.add_vectors(ids=ids, embeddings=embeddings, documents=chunks)

        return {
            "total_chunks": len(chunks),
            "_log": {
                "pages": len(pages_list),
                "chunks": len(chunks),
                "embeddings": len(embeddings),
                "persisted": len(ids),
            },
        }
