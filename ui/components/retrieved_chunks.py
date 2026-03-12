from typing import Iterable, Mapping

import streamlit as st

from ..utils.formatters import format_chunk


def render_retrieved_chunks(chunks: Iterable[Mapping] | None, show_scores: bool = True) -> None:
    """Renderiza os chunks recuperados com metadados básicos."""
    st.subheader("Chunks recuperados")
    if not chunks:
        st.write("Nenhum chunk disponível.")
        return

    for raw in chunks:
        c = format_chunk(dict(raw))
        st.markdown(f"**{c['reference']}**")
        if show_scores:
            st.caption(
                f"score: {c['score']!r} | rerank_score: {c['rerank_score']!r}"
            )
        st.write(c["text_preview"])
        st.markdown("---")

