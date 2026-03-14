"""
Serviço de embeddings: única responsabilidade é calcular vetores.
Usado pelo pipeline de ingestão (após metadata enricher) e pelo pipeline de retrieval (embed da pergunta).
"""
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings


class EmbeddingService:
    """Calcula embeddings para documentos e para a pergunta. Única camada que gera vetores."""

    def __init__(self) -> None:
        self._model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model_name,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Retorna lista de vetores, um por texto."""
        if not texts:
            return []
        return self._model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """Retorna o vetor da query (ex.: pergunta)."""
        return self._model.embed_query(text)
