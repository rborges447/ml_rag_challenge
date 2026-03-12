from typing import Iterable

import streamlit as st


def render_references(references: Iterable[str] | None) -> None:
    """Renderiza a lista de referências."""
    st.subheader("Referências")
    if not references:
        st.write("Nenhuma referência disponível.")
        return

    for ref in references:
        st.markdown(f"- {ref}")

