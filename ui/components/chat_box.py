from typing import List, Mapping

import streamlit as st


def render_chat_box(messages: List[Mapping[str, str]]) -> None:
    """Renderiza o histórico de mensagens Q/A."""
    if not messages:
        st.info("Nenhuma pergunta ainda. Faça sua primeira pergunta!")
        return

    for item in messages:
        question = item.get("question", "")
        answer = item.get("answer", "")
        st.markdown(f"**Q:** {question}")
        st.markdown(f"**A:** {answer}")
        st.markdown("---")

