"""
Pipeline 2 — Retrieval: orquestra explicitamente embed → search → filter → dedup → rerank → format.
"""
from langchain_core.documents import Document

from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.services.embeddings import EmbeddingService
from app.services.retrieval.ranking_service import rerank
from app.services.retrieval.retrieval_helpers import (
    _deduplicate_by_similarity,
    _distance_to_score,
)


class RetrievalPipeline:
    """Orquestra o fluxo de retrieval: cada passo explícito (embed → search → filter → dedup → rerank → format)."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store=None,
    ) -> None:
        self._embedding_service = embedding_service or EmbeddingService()
        self._vector_store = vector_store or get_vector_store()

    def run(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> list[dict]:
        """Executa o pipeline: embed → search → filter → dedup → rerank → format. Retorna lista de chunks."""
        # 1. Config
        initial_k = initial_k if initial_k is not None else settings.retrieval_initial_k
        top_k = top_k if top_k is not None else settings.retrieval_top_k_final
        max_distance = max_distance if max_distance is not None else settings.retrieval_max_distance
        min_score = min_score if min_score is not None else settings.retrieval_min_score

        # 2. Embed da pergunta
        query_embedding = self._embedding_service.embed_query(question)

        # 3. Busca por vetor
        results = self._vector_store.similarity_search_with_score_by_vector(
            query_embedding, k=initial_k
        )

        # 4. Filtrar por max_distance e conteúdo não vazio
        candidates = [
            (doc, distance)
            for doc, distance in results
            if (max_distance is None or distance <= max_distance)
            and (doc.page_content or "").strip()
        ]

        # 5. Deduplicar
        candidates = _deduplicate_by_similarity(candidates)

        # 6. Rerank
        reranked = rerank(question, candidates)

        # 7. Formatar (top_k, min_score)
        retrieved_chunks: list[dict] = []
        for doc, distance, rerank_score in reranked:
            if min_score is not None and rerank_score < min_score:
                continue
            if len(retrieved_chunks) >= top_k:
                break
            text = (doc.page_content or "").strip()
            meta = doc.metadata or {}
            retrieved_chunks.append({
                "text": text,
                "source": meta.get("source"),
                "page": meta.get("page"),
                "distance": distance,
                "score": _distance_to_score(distance),
                "rerank_score": rerank_score,
                "chunk_index": meta.get("chunk_index"),
                "char_count": meta.get("char_count"),
                "is_intro_page": meta.get("is_intro_page"),
                "section_hint": meta.get("section_hint"),
            })
        return retrieved_chunks
