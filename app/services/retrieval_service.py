"""
Serviço de retrieval usando o vector store (LangChain/Chroma).
Formata resultados com text, source, page, distance, score e deduplica por texto.
Preparado para futura adição de reranker (método ou pipeline separado).
"""
from app.services.vector_store import VectorStore


def _distance_to_score(distance: float) -> float:
    """Converte distância L2 em score (maior = mais similar)."""
    return 1.0 / (1.0 + distance)


class RetrievalService:
    """Recupera chunks relevantes para uma pergunta via vector store."""

    def __init__(self) -> None:
        self._vector_store = VectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 8,
        max_distance: float | None = None,
    ) -> list[dict]:
        """
        Retorna lista de chunks com text, source, page, distance, score.
        Aplica deduplicação por texto e opcional filtro por max_distance.
        """
        # Buscar um pouco a mais para compensar deduplicação
        k = min(top_k * 2, 50)
        results = self._vector_store.similarity_search_with_score(question, k=k)

        retrieved_chunks: list[dict] = []
        seen_texts: set[str] = set()

        for doc, distance in results:
            if max_distance is not None and distance > max_distance:
                continue

            text = (doc.page_content or "").strip()
            if not text or text in seen_texts:
                continue
            seen_texts.add(text)

            metadata = doc.metadata or {}
            retrieved_chunks.append(
                {
                    "text": text,
                    "source": metadata.get("source"),
                    "page": metadata.get("page"),
                    "distance": distance,
                    "score": _distance_to_score(distance),
                }
            )
            if len(retrieved_chunks) >= top_k:
                break

        return retrieved_chunks
