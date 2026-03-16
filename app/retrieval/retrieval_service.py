"""
RetrievalService: embed (query e documentos), vector search, filter, dedup, rerank.
O embedding é lógica interna (módulo retrieval/embedding.py); expõe embed_documents para ingestão.
"""
from langchain_core.documents import Document

from app.retrieval.embedding import _EmbeddingModel
from app.retrieval.ranking_service import rerank
from app.retrieval.retrieval_helpers import _deduplicate_by_similarity, _distance_to_score


class RetrievalService:
    """Concentra toda a responsabilidade de retrieval; usa o módulo embedding internamente."""

    def __init__(self, vector_store) -> None:
        self._vector_store = vector_store
        self._embedding = _EmbeddingModel()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Retorna lista de vetores, um por texto. Exposto para o pipeline de ingestão."""
        return self._embedding.embed_documents(texts)

    def _embed_query(self, text: str) -> list[float]:
        """Retorna o vetor da query (ex.: pergunta). Uso interno em retrieve()."""
        return self._embedding.embed_query(text)

    def retrieve(
        self,
        question: str,
        top_k: int,
        initial_k: int,
        max_distance: float | None,
        min_score: float | None,
    ) -> list[dict]:
        """
        Embed da pergunta, busca no vector store, filter, dedup, rerank.
        Retorna list[dict] no formato retrieved_chunks (text, source, page, distance, score, rerank_score, ...).
        """
        query_embedding = self._embed_query(question)
        raw_results = self._vector_store.query_nearest(query_embedding, k=initial_k)

        candidates: list[tuple[Document, float]] = []
        for text, meta, dist in raw_results:
            doc = Document(page_content=text or "", metadata=meta)
            if (max_distance is not None and dist > max_distance) or not (doc.page_content or "").strip():
                continue
            candidates.append((doc, dist))

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
