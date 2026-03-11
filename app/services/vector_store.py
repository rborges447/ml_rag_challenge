"""
Vector store que encapsula Chroma via LangChain.
Expõe interface do projeto: add_documents, get_retriever, similarity_search_with_score.
"""
import uuid

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.core.config import settings


class VectorStore:
    """Encapsula Chroma (LangChain) com HuggingFaceEmbeddings."""

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
        embedding_model_name: str | None = None,
    ) -> None:
        self._persist_directory = persist_directory or settings.chroma_path
        self._collection_name = collection_name or settings.chroma_collection_name
        self._embedding_model_name = (
            embedding_model_name or settings.embedding_model_name
        )
        self._embeddings = HuggingFaceEmbeddings(
            model_name=self._embedding_model_name,
        )
        self._store = Chroma(
            collection_name=self._collection_name,
            embedding_function=self._embeddings,
            persist_directory=self._persist_directory,
        )

    def add_documents(self, documents: list[Document]) -> list[str]:
        """
        Indexa documentos no Chroma. Gera ids únicos para cada documento.
        Retorna a lista de ids gerados.
        """
        if not documents:
            return []
        ids = [str(uuid.uuid4()) for _ in documents]
        self._store.add_documents(documents, ids=ids)
        return ids

    def get_retriever(self, k: int = 8, **kwargs: object) -> object:
        """Retorna um retriever LangChain para uso externo."""
        return self._store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k, **kwargs},
        )

    def similarity_search_with_score(
        self, query: str, k: int = 8
    ) -> list[tuple[Document, float]]:
        """
        Busca por similaridade retornando (Document, score).
        O score do Chroma é distância L2 (menor = mais similar).
        """
        return self._store.similarity_search_with_score(query, k=k)
