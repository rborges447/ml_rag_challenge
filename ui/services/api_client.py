from typing import Any, Dict, List, Optional, Tuple

import httpx

from ..config.settings import get_settings


def _get_client(timeout_seconds: int) -> httpx.Client:
    return httpx.Client(timeout=timeout_seconds)


def health_check() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Consulta o endpoint /health da API.
    Retorna (dados, erro).
    """
    settings = get_settings()
    try:
        with _get_client(settings.http_timeout_seconds) as client:
            response = client.get(f"{settings.api_base_url}/health")
        if response.status_code != 200:
            return None, f"Erro {response.status_code}: {response.text}"
        return response.json(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Falha ao consultar /health: {exc}"


def upload_document(file_obj) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Envia um único arquivo PDF para /documents.
    `file_obj` deve expor .name e .getvalue() (como UploadedFile do Streamlit).
    Retorna (dados_json, erro).
    """
    settings = get_settings()
    try:
        files = {
            "file": (
                getattr(file_obj, "name", "document.pdf"),
                file_obj.getvalue(),
                "application/pdf",
            )
        }
        with _get_client(settings.http_timeout_seconds) as client:
            response = client.post(f"{settings.api_base_url}/documents", files=files)
        if response.status_code != 200:
            return None, f"Erro {response.status_code}: {response.text}"
        return response.json(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Falha ao enviar documento: {exc}"


def ask_question(
    question: str,
    top_k: Optional[int] = None,
    initial_k: Optional[int] = None,
    max_distance: Optional[float] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Envia uma pergunta para /question.
    Retorna (dados_json, erro).
    """
    if not question.strip():
        return None, "Pergunta vazia."

    settings = get_settings()
    params: Dict[str, Any] = {}
    if top_k is not None:
        params["top_k"] = top_k
    if initial_k is not None:
        params["initial_k"] = initial_k
    if max_distance is not None:
        params["max_distance"] = max_distance

    try:
        payload = {"question": question}
        with _get_client(settings.http_timeout_seconds) as client:
            response = client.post(
                f"{settings.api_base_url}/question",
                json=payload,
                params=params or None,
            )
        if response.status_code != 200:
            return None, f"Erro {response.status_code}: {response.text}"
        return response.json(), None
    except Exception as exc:  # noqa: BLE001
        return None, f"Falha ao chamar /question: {exc}"

