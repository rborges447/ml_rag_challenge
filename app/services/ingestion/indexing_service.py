"""
Encapsula a persistência dos chunks no vector store.
"""
from typing import TYPE_CHECKING

from langchain_core.documents import Document

from app.core.dependencies import get_vector_store

if TYPE_CHECKING:
    from app.services.vector_store import VectorStore


class IndexingService:
    """Recebe chunks e persiste via vector_store.add_documents."""

    def __init__(self, vector_store: "VectorStore | None" = None) -> None:
        self._vector_store = vector_store or get_vector_store()

    def index(self, chunks: list[Document]) -> list[str]:
        """Indexa os chunks no vector store. Retorna a lista de ids gerados."""
        return self._vector_store.add_documents(chunks)
