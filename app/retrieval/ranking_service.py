"""
Reranking heurístico: bônus por termos da pergunta, definições e padrões; penalizações por chunk curto, genérico, intro.
"""
import re
import unicodedata
from difflib import SequenceMatcher

from langchain_core.documents import Document

from app.core.logging import get_logger

logger = get_logger(__name__)


def _normalize_for_match(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    nfd = unicodedata.normalize("NFD", s)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def _tokenize(s: str) -> set[str]:
    s = _normalize_for_match(s)
    return set(re.findall(r"[a-z0-9]{2,}", s))


def _text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.strip(), b.strip()).ratio()


def _vector_score(distance: float) -> float:
    return 1.0 / (1.0 + distance)


BONUS_TERM_PRESENT = 0.08
BONUS_CAP_TERMS = 0.35
BONUS_DEFINITION_PATTERN = 0.25
BONUS_EXACT_PHRASE = 0.2
PENALTY_SHORT_CHUNK = 0.12
PENALTY_TITLE_ONLY = 0.1
PENALTY_INTRO_PAGE = 0.15
PENALTY_NEAR_DUPLICATE = 0.2
MIN_CHARS_FOR_PENALTY = 100
TITLE_LINE_MAX_CHARS = 80
NEAR_DUPLICATE_THRESHOLD = 0.88


def _is_definition_question(query: str) -> bool:
    q = _normalize_for_match(query)
    return "o que e " in q or "o que sao " in q or "o que é " in q or "qual e " in q or "quais sao " in q


def _extract_definition_target(query: str) -> str | None:
    q = query.strip().lower()
    for prefix in ("o que é ", "o que e ", "o que são ", "o que sao ", "qual é ", "qual e ", "quais são ", "quais sao "):
        if q.startswith(prefix):
            return q[len(prefix):].strip().rstrip("?")
    return None


def _has_definition_pattern(chunk_text: str, target: str | None) -> bool:
    if not chunk_text or not target:
        return False
    text = _normalize_for_match(chunk_text)
    target_norm = _normalize_for_match(target)
    if not target_norm:
        return False
    patterns = [
        f"{target_norm} e ", f"{target_norm} sao ",
        "define-se ", "e definido como ", "e a maquina ", "sao aqueles ",
    ]
    return any(p in text for p in patterns)


def _has_exact_phrase(chunk_text: str, phrase: str) -> bool:
    if not phrase or not chunk_text:
        return False
    return _normalize_for_match(phrase) in _normalize_for_match(chunk_text)


def _looks_like_title_only(chunk_text: str) -> bool:
    if not chunk_text:
        return True
    lines = [ln.strip() for ln in chunk_text.split("\n") if ln.strip()]
    if not lines:
        return True
    if len(lines) == 1 and len(lines[0]) <= TITLE_LINE_MAX_CHARS:
        return True
    if re.match(r"^\d+[\.\)]\s*", lines[0]) and len(lines[0]) < 60:
        return True
    return False


def rerank(
    query: str,
    candidates: list[tuple[Document, float]],
    penalty_near_duplicate: bool = True,
) -> list[tuple[Document, float, float]]:
    """Retorna lista de (Document, distance_original, rerank_score). Ordenado por rerank_score decrescente."""
    logger.debug("rerank candidatos=%s", len(candidates))
    if not candidates:
        return []
    query_tokens = _tokenize(query)
    definition_target = _extract_definition_target(query) if _is_definition_question(query) else None
    scored: list[tuple[Document, float, float]] = []

    for doc, distance in candidates:
        text = (doc.page_content or "").strip()
        meta = doc.metadata or {}
        rerank_s = _vector_score(distance)
        chunk_tokens = _tokenize(text)
        overlap = query_tokens & chunk_tokens
        rerank_s += min(len(overlap) * BONUS_TERM_PRESENT, BONUS_CAP_TERMS)
        if definition_target and _has_definition_pattern(text, definition_target):
            rerank_s += BONUS_DEFINITION_PATTERN
        if _has_exact_phrase(text, query):
            rerank_s += BONUS_EXACT_PHRASE
        if meta.get("char_count", len(text)) < MIN_CHARS_FOR_PENALTY:
            rerank_s -= PENALTY_SHORT_CHUNK
        if _looks_like_title_only(text):
            rerank_s -= PENALTY_TITLE_ONLY
        if meta.get("is_intro_page") is True:
            rerank_s -= PENALTY_INTRO_PAGE
        scored.append((doc, distance, max(0.0, rerank_s)))

    if penalty_near_duplicate and len(scored) > 1:
        texts = [s[0].page_content or "" for s in scored]
        for i in range(len(scored)):
            for j in range(len(scored)):
                if i >= j:
                    continue
                if _text_similarity(texts[i], texts[j]) >= NEAR_DUPLICATE_THRESHOLD:
                    if scored[i][2] < scored[j][2]:
                        doc, dist, rs = scored[i]
                        scored[i] = (doc, dist, max(0.0, rs - PENALTY_NEAR_DUPLICATE))
                    else:
                        doc, dist, rs = scored[j]
                        scored[j] = (doc, dist, max(0.0, rs - PENALTY_NEAR_DUPLICATE))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored


class RankingService:
    """Encapsula a lógica de reranking. Expõe o método rerank."""

    def rerank(
        self,
        query: str,
        candidates: list[tuple[Document, float]],
        penalty_near_duplicate: bool = True,
    ) -> list[tuple[Document, float, float]]:
        return rerank(query, candidates, penalty_near_duplicate=penalty_near_duplicate)
