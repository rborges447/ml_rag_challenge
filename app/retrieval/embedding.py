"""
Lógica de embedding dentro do pacote retrieval (uso interno; não exportada no __init__).
"""
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class _EmbeddingModel:
    """Encapsula o modelo de embeddings (HuggingFace). Uso interno pelo RetrievalService."""

    def __init__(self) -> None:
        self._model = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Retorna lista de vetores, um por texto."""
        if not texts:
            return []
        out = self._model.embed_documents(texts)
        logger.debug("embed_documents count=%s", len(out))
        return out

    def embed_query(self, text: str) -> list[float]:
        """Retorna o vetor da query (ex.: pergunta)."""
        logger.debug("embed_query")
        return self._model.embed_query(text)
