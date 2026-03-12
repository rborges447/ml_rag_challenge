import pathlib
import importlib.util

import streamlit as st

from .components.sidebar import render_sidebar
from .state.session_state import init_session_state


BASE_DIR = pathlib.Path(__file__).resolve().parent


def _load_page_module(name: str, filename: str):
    """Carrega um módulo de página Streamlit a partir de ui/pages/filename."""
    file_path = BASE_DIR / "pages" / filename
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader  # for type checkers
    spec.loader.exec_module(module)
    return module


def main() -> None:
    st.set_page_config(
        page_title="RAG UI",
        page_icon="💬",
        layout="wide",
    )

    init_session_state()
    render_sidebar()

    st.title("RAG UI")

    tab_upload, tab_chat = st.tabs(
        ["Upload de documentos", "Chat de perguntas e respostas"]
    )

    with tab_upload:
        upload_page = _load_page_module("upload_page", "1_upload.py")
        upload_page.main()

    with tab_chat:
        chat_page = _load_page_module("chat_page", "2_chat.py")
        chat_page.main()


if __name__ == "__main__":
    main()

