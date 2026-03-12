"""
Prepara contexto a partir dos chunks recuperados (concatenação). Extensível para QA/LLM.
"""


def build_context(
    chunks: list[dict],
    separator: str = "\n\n",
    max_chars: int | None = None,
) -> str:
    """
    Concatena o campo "text" dos chunks. Se max_chars for informado, trunca o resultado.
    Útil para montagem de contexto em prompts futuros.
    """
    texts = [c.get("text", "") or "" for c in chunks]
    context = separator.join(texts)
    if max_chars is not None and len(context) > max_chars:
        context = context[:max_chars].rsplit(" ", 1)[0] if max_chars > 0 else ""
    return context


class ContextBuilder:
    """Prepara contexto para uso em QA/LLM."""

    def build(
        self,
        chunks: list[dict],
        separator: str = "\n\n",
        max_chars: int | None = None,
    ) -> str:
        return build_context(chunks, separator=separator, max_chars=max_chars)
