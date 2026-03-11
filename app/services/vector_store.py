"""
Vector store que encapsula Chroma via LangChain.
Expõe interface do projeto: add_documents, get_retriever, similarity_search_with_score.
Recebe embedding_function de forma injetável; se não for passado, usa default (HuggingFaceEmbeddings).
"""
import uuid
from typing import TYPE_CHECKING

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.core.config import settings

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings


class VectorStore:
    """Encapsula Chroma (LangChain). Embedding pode ser injetado ou usa default."""

    def __init__(
        self,
        embedding_function: "Embeddings | None" = None,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self._persist_directory = persist_directory or settings.chroma_path
        self._collection_name = collection_name or settings.chroma_collection_name
        if embedding_function is None:
            embedding_function = HuggingFaceEmbeddings(
                model_name=settings.embedding_model_name,
            )
        self._store = Chroma(
            collection_name=self._collection_name,
            embedding_function=embedding_function,
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
        Busca por similaridade retornando (Document, distance).
        O valor retornado pelo Chroma é distância L2 (menor = mais similar).
        """
        return self._store.similarity_search_with_score(query, k=k)
