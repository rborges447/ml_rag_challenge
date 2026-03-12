import streamlit as st

from ui.components.chat_box import render_chat_box
from ui.components.references import render_references
from ui.components.retrieved_chunks import render_retrieved_chunks
from ui.services import api_client
from ui.state import session_state as ui_state


def main() -> None:
    ui_state.init_session_state()

    st.title("Chat RAG")
    st.caption("Pergunte sobre os documentos indexados.")

    messages = st.session_state.get("chat_messages", [])
    render_chat_box(messages)

    question = st.text_input("Pergunta", placeholder="Digite sua pergunta aqui...")

    col_send, _ = st.columns([1, 3])
    with col_send:
        send = st.button("Enviar")

    if send and question:
        with st.spinner("Consultando API..."):
            data, error = api_client.ask_question(question)

        if error:
            st.error(error)
        elif data is not None:
            answer = data.get("answer", "")
            references = data.get("references") or []
            chunks = data.get("retrieved_chunks") or []

            ui_state.append_message(question, answer)
            st.session_state["last_references"] = references
            st.session_state["last_retrieved_chunks"] = chunks

            st.rerun()

    # Se houver dados do último resultado, renderiza referências e chunks
    references = st.session_state.get("last_references")
    chunks = st.session_state.get("last_retrieved_chunks")

    if references is not None:
        render_references(references)

    if chunks is not None and st.session_state.get("show_chunks", True):
        render_retrieved_chunks(chunks, show_scores=True)


if __name__ == "__main__":
    main()

