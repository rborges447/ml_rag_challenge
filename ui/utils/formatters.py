from typing import Any, Dict


def format_reference(source: str | None, page: Any) -> str:
    if not source:
        return "Fonte desconhecida"
    if page is None:
        return f"{source}"
    return f"{source} - página {page}"


def shorten_text(text: str, max_chars: int = 400) -> str:
    text = text or ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def format_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "reference": format_reference(chunk.get("source"), chunk.get("page")),
        "score": chunk.get("score"),
        "rerank_score": chunk.get("rerank_score"),
        "text_preview": shorten_text(chunk.get("text", "")),
    }

