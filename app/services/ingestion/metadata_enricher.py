"""
Enriquecimento de metadados nos chunks: chunk_id, chunk_index, char_count, is_intro_page, section_hint.
"""
import re
import uuid

from langchain_core.documents import Document

from app.core.config import settings


def _is_intro_page(page: int, text: str) -> bool:
    if page <= getattr(settings, "intro_page_max", 2):
        return True
    lower = text.lower()[:1500]
    intro_markers = ("introdução", "introducao", "sumário", "sumario", "capítulo 1", "capitulo 1")
    if any(m in lower for m in intro_markers) and len(text.split()) < 200:
        return True
    return False


def _section_hint(chunk_text: str) -> str:
    if not chunk_text or len(chunk_text) < 10:
        return ""
    first_line = chunk_text.split("\n")[0].strip()
    if len(first_line) > 60 or not first_line:
        return ""
    if re.match(r"^[\d\.\-\s]+\s*$", first_line):
        return ""
    return first_line[:100]


class MetadataEnricher:
    """Adiciona metadados úteis em cada chunk (in-place)."""

    def enrich(self, chunks: list[Document]) -> None:
        for i, chunk in enumerate(chunks):
            text = chunk.page_content or ""
            meta = chunk.metadata or {}
            page = meta.get("page", 0)
            meta["chunk_id"] = str(uuid.uuid4())
            meta["chunk_index"] = i
            meta["char_count"] = len(text)
            meta["is_intro_page"] = _is_intro_page(page, text)
            meta["section_hint"] = _section_hint(text)
            chunk.metadata = meta
