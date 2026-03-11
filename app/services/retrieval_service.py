"""
Serviço de retrieval em duas etapas: busca ampla no Chroma + reranking heurístico.
Retorna chunks com text, source, page, distance, score, rerank_score e metadados.
"""
from difflib import SequenceMatcher

from langchain_core.documents import Document

from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.services.reranker import rerank


def _distance_to_score(distance: float) -> float:
    """Converte distância L2 em score (maior = mais similar)."""
    return 1.0 / (1.0 + distance)


def _text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.strip(), b.strip()).ratio()


def _deduplicate_by_similarity(
    candidates: list[tuple[Document, float]],
    threshold: float = 0.9,
) -> list[tuple[Document, float]]:
    """Mantém apenas um de cada par com similaridade de texto acima do threshold (melhor score vetorial)."""
    if len(candidates) <= 1:
        return candidates
    out: list[tuple[Document, float]] = []
    for doc, dist in candidates:
        text = (doc.page_content or "").strip()
        skip = False
        for existing_doc, existing_dist in out:
            if _text_similarity(text, (existing_doc.page_content or "").strip()) >= threshold:
                skip = True
                break
        if not skip:
            out.append((doc, dist))
    return out


class RetrievalService:
    """Recupera chunks relevantes: busca initial_k, rerank, retorna top_k_final."""

    def __init__(self):
        self._vector_store = get_vector_store()

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> list[dict]:
        """
        Etapa 1: similarity_search_with_score(question, k=initial_k).
        Filtro max_distance; deduplicação por similaridade.
        Etapa 2: rerank heurístico.
        Etapa 3: ordenar por rerank_score, filtrar min_score, cortar top_k.
        Retorna list[dict] com text, source, page, distance, score, rerank_score e metadados.
        """
        initial_k = initial_k if initial_k is not None else settings.retrieval_initial_k
        top_k = top_k if top_k is not None else settings.retrieval_top_k_final
        max_distance = max_distance if max_distance is not None else settings.retrieval_max_distance
        min_score = min_score if min_score is not None else settings.retrieval_min_score

        results = self._vector_store.similarity_search_with_score(question, k=initial_k)

        candidates: list[tuple[Document, float]] = []
        for doc, distance in results:
            if max_distance is not None and distance > max_distance:
                continue
            text = (doc.page_content or "").strip()
            if not text:
                continue
            candidates.append((doc, distance))

        candidates = _deduplicate_by_similarity(candidates)

        reranked = rerank(question, candidates)

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
