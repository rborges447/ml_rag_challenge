"""
Helpers de retrieval: dedup e conversão de distância para score.
Usados pelo RetrievalPipeline.
"""
from difflib import SequenceMatcher

from langchain_core.documents import Document


def _distance_to_score(distance: float) -> float:
    return 1.0 / (1.0 + distance)


def _text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.strip(), b.strip()).ratio()


def _deduplicate_by_similarity(
    candidates: list[tuple[Document, float]],
    threshold: float = 0.9,
) -> list[tuple[Document, float]]:
    if len(candidates) <= 1:
        return candidates
    out: list[tuple[Document, float]] = []
    for doc, dist in candidates:
        text = (doc.page_content or "").strip()
        skip = any(
            _text_similarity(text, (existing_doc.page_content or "").strip()) >= threshold
            for existing_doc, _ in out
        )
        if not skip:
            out.append((doc, dist))
    return out
