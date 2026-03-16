"""
Serviço de processamento de documentos: loader → preprocessor → chunking → metadata enricher.

Transforma um arquivo PDF em uma lista de chunks enriquecidos, sem integrar com
serviços externos (embeddings, vector store, retrieval).
"""

from langchain_core.documents import Document

from app.document_processor.chunking_service import ChunkingService
from app.document_processor.document_loader_service import DocumentLoaderService
from app.document_processor.metadata_enricher import MetadataEnricher
from app.document_processor.text_preprocessor import TextPreprocessor


class DocumentProcessingService:
    """
    Serviço de domínio de processamento de documentos.

    Responsável por:
    - carregar o documento bruto,
    - preprocessar páginas,
    - transformar páginas em `Document`,
    - fazer chunking,
    - enriquecer metadados dos chunks.

    Não conhece nem integra com RetrievalService, embeddings ou VectorStore.
    """

    def __init__(self) -> None:
        self._loader = DocumentLoaderService()
        self._preprocessor = TextPreprocessor()
        self._chunking = ChunkingService()
        self._metadata_enricher = MetadataEnricher()

    def run(
        self,
        file_path: str,
        source_name: str,
        request_id: str | None = None,
    ) -> dict:
        """
        Executa o fluxo interno de processamento: carrega PDF, preprocessa, faz chunking
        e enriquece metadados.

        Retorna um dicionário com:
        - "chunks": lista de Document enriquecidos,
        - "_log": {"pages": int, "chunks": int}.
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

        return {
            "chunks": chunks,
            "_log": {
                "pages": len(pages_list),
                "chunks": len(chunks),
            },
        }

