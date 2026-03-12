from typing import Any, Dict, List

import streamlit as st


def init_session_state() -> None:
    """Inicializa todas as chaves usadas pela UI no session_state."""
    defaults: Dict[str, Any] = {
        "chat_messages": [],  # list[dict[str, str]] com question/answer
        "last_references": None,  # list[str] | None
        "last_retrieved_chunks": None,  # list[dict] | None
        "api_status": "unknown",  # unknown | up | down
        "upload_feedback": [],  # list[dict]
        "show_chunks": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def append_message(question: str, answer: str) -> None:
    init_session_state()
    st.session_state["chat_messages"].append(
        {"question": question, "answer": answer}
    )


def set_api_status(status: str) -> None:
    init_session_state()
    st.session_state["api_status"] = status


def add_upload_feedback(entry: Dict[str, Any]) -> None:
    init_session_state()
    st.session_state["upload_feedback"].append(entry)


def clear_conversation() -> None:
    init_session_state()
    st.session_state["chat_messages"] = []
    st.session_state["last_references"] = None
    st.session_state["last_retrieved_chunks"] = None

