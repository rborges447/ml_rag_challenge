"""
Pipeline de pergunta: embed query → search → filter → dedup → rerank → format → prompt → LLM → references.
Centraliza o fluxo completo da pergunta (substitui RetrievalPipeline + GenerationPipeline + AnswerQuestionUseCase).
"""
import time

from app.clients import LLMClient
from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.core.logging import get_logger
from app.embeddings import EmbeddingService
from app.qa.prompt_builder import build_prompt
from app.retrieval.ranking_service import rerank
from app.retrieval.retrieval_helpers import _deduplicate_by_similarity, _distance_to_score


def _truncate(s: str, max_len: int = 80) -> str:
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."


logger = get_logger(__name__)


class QuestionPipeline:
    """Orquestra o fluxo completo da pergunta: retrieval + geração + montagem de referências."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store=None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self._embedding_service = embedding_service or EmbeddingService()
        self._vector_store = vector_store or get_vector_store()
        self._llm_client = llm_client or LLMClient()

    def run(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
        request_id: str | None = None,
    ) -> dict:
        """
        Retorna {"answer": str, "references": list[str], "retrieved_chunks": list[dict]}.
        """
        t0 = time.perf_counter()
        rid = request_id or ""
        logger.info(
            "request_id=%s | question pipeline início pergunta=%s",
            rid,
            _truncate(question),
        )

        initial_k = initial_k if initial_k is not None else settings.retrieval_initial_k
        top_k = top_k if top_k is not None else settings.retrieval_top_k_final
        max_distance = max_distance if max_distance is not None else settings.retrieval_max_distance
        min_score = min_score if min_score is not None else settings.retrieval_min_score

        query_embedding = self._embedding_service.embed_query(question)
        results = self._vector_store.similarity_search_with_score_by_vector(
            query_embedding, k=initial_k
        )

        candidates = [
            (doc, distance)
            for doc, distance in results
            if (max_distance is None or distance <= max_distance)
            and (doc.page_content or "").strip()
        ]
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

        logger.info(
            "request_id=%s | resultados recuperados=%s",
            rid,
            len(retrieved_chunks),
        )
        logger.debug("request_id=%s | montando prompt com %s chunks", rid, len(retrieved_chunks))
        prompt = build_prompt(question, retrieved_chunks)
        logger.info("request_id=%s | chamando LLM", rid)
        answer = self._llm_client.generate(prompt)

        references_set: set[str] = set()
        for chunk in retrieved_chunks:
            source = chunk.get("source")
            page = chunk.get("page")
            if source is not None and page is not None:
                references_set.add(f"{source} - page {page}")
        references = sorted(references_set)
        logger.info("request_id=%s | referências finais=%s", rid, len(references))

        elapsed = time.perf_counter() - t0
        logger.info("request_id=%s | pipeline concluído elapsed=%.3fs", rid, elapsed)

        return {
            "answer": answer,
            "references": references,
            "retrieved_chunks": retrieved_chunks,
        }
