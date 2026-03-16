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
        Executa o fluxo interno de processamento: carrega PDF (table-aware), preprocessa
        apenas texto narrativo, faz chunking só em narrativo, e mantém cada tabela como
        um chunk único (cabeçalho + linhas). Enriquece metadados de todos os chunks.
        """
        blocks = self._loader.load(file_path, source_name)
        table_blocks = [b for b in blocks if b.get("is_table")]
        narrative_blocks = [b for b in blocks if not b.get("is_table")]

        narrative_preprocessed = self._preprocessor.preprocess_pages(narrative_blocks)

        documents_for_split = []
        for p in narrative_preprocessed:
            page_num = p["page"]
            text = p.get("text", "")
            if not text.strip():
                continue
            documents_for_split.append(
                Document(
                    page_content=text,
                    metadata={"source": source_name, "page": page_num, "is_table": False},
                )
            )

        chunks_narrative = self._chunking.split(documents_for_split) if documents_for_split else []

        table_chunks = []
        for b in table_blocks:
            text = b.get("text", "")
            if not text.strip():
                continue
            table_chunks.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": source_name,
                        "page": b["page"],
                        "is_table": True,
                    },
                )
            )

        chunks = chunks_narrative + table_chunks
        self._metadata_enricher.enrich(chunks)

        unique_pages = len({p["page"] for p in blocks})
        return {
            "chunks": chunks,
            "_log": {
                "pages": unique_pages,
                "chunks": len(chunks),
            },
        }

