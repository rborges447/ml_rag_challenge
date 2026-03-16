"""
Lógica de embedding dentro do pacote retrieval (uso interno; não exportada no __init__).
Modelos E5 (intfloat/multilingual-e5-*) exigem prefixo: "query: " para query, "passage: " para documentos.
"""
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

E5_QUERY_PREFIX = "query: "
E5_PASSAGE_PREFIX = "passage: "


def _is_e5_model(name: str) -> bool:
    """True se o modelo for da família E5 (ex.: multilingual-e5-base), que exige prefixos."""
    if not name:
        return False
    n = name.lower()
    return "e5" in n or "multilingual-e5" in n


class _EmbeddingModel:
    """Encapsula o modelo de embeddings (HuggingFace). Uso interno pelo RetrievalService."""

    def __init__(self) -> None:
        self._model = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
        self._use_e5_prefix = _is_e5_model(settings.embedding_model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Retorna lista de vetores, um por texto."""
        if not texts:
            return []
        if self._use_e5_prefix:
            texts = [E5_PASSAGE_PREFIX + (t or "") for t in texts]
        out = self._model.embed_documents(texts)
        logger.debug("embed_documents count=%s", len(out))
        return out

    def embed_query(self, text: str) -> list[float]:
        """Retorna o vetor da query (ex.: pergunta)."""
        logger.debug("embed_query")
        if self._use_e5_prefix:
            text = E5_QUERY_PREFIX + (text or "")
        return self._model.embed_query(text)
