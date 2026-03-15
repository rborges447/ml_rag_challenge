"""
Vector store que encapsula Chroma: apenas armazenamento e consulta de vetores.
Não calcula embeddings; recebe vetores já calculados pelo EmbeddingService.
"""
import chromadb
from langchain_core.documents import Document

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Encapsula Chroma. Apenas persiste e consulta vetores (ids, embeddings, documents, metadatas)."""

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self._persist_directory = persist_directory or settings.chroma_path
        self._collection_name = collection_name or settings.chroma_collection_name
        self._client = chromadb.PersistentClient(path=self._persist_directory)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "l2"},
        )

    def add_vectors(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[Document],
    ) -> list[str]:
        """
        Indexa vetores no Chroma. Os vetores devem ter sido calculados pelo EmbeddingService.
        Retorna a lista de ids.
        """
        if not documents or not embeddings or not ids:
            return []
        if len(ids) != len(embeddings) or len(ids) != len(documents):
            raise ValueError("ids, embeddings e documents devem ter o mesmo tamanho")
        texts = [doc.page_content for doc in documents]
        metadatas = []
        for doc in documents:
            meta = {}
            for k, v in (doc.metadata or {}).items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
            metadatas.append(meta)
        self._collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        logger.info("add_vectors quantidade=%s", len(ids))
        return ids

    def similarity_search_with_score_by_vector(
        self,
        query_embedding: list[float],
        k: int = 8,
    ) -> list[tuple[Document, float]]:
        """
        Busca por similaridade usando o vetor da pergunta (já calculado pelo EmbeddingService).
        Retorna (Document, distance) com distância L2 (menor = mais similar).
        """
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        out: list[tuple[Document, float]] = []
        if not result or not result["ids"] or not result["ids"][0]:
            return out
        docs = result["documents"][0]
        metadatas = result["metadatas"][0] or []
        distances = result["distances"][0]
        for i, doc_text in enumerate(docs):
            meta = metadatas[i] if i < len(metadatas) else {}
            dist = float(distances[i]) if i < len(distances) else 0.0
            out.append((
                Document(page_content=doc_text or "", metadata=meta),
                dist,
            ))
        logger.info("similarity_search_with_score_by_vector k=%s resultados=%s", k, len(out))
        return out
