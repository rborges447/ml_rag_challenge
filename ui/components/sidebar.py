import streamlit as st

from ..services import api_client
from ..state import session_state as ui_state


def render_sidebar() -> None:
    """Sidebar com status da API, config e ações globais."""
    st.sidebar.header("Configuração & Status")

    # Health check
    data, error = api_client.health_check()
    if error:
        ui_state.set_api_status("down")
        st.sidebar.error(f"API indisponível: {error}")
    else:
        ui_state.set_api_status("up")
        status = data.get("status", "ok") if isinstance(data, dict) else "ok"
        st.sidebar.success(f"API OK ({status})")

    st.sidebar.markdown("---")

    if st.sidebar.button("Limpar conversa"):
        ui_state.clear_conversation()
        st.rerun()

    show_chunks = st.sidebar.checkbox("Mostrar chunks recuperados", value=True)
    st.session_state["show_chunks"] = show_chunks

