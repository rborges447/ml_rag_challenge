"""
Config e dependências (settings, vector store, retrieval).
"""
from app.core.config import settings, Settings
from app.core.dependencies import (
    get_retrieval_service,
    get_settings,
    get_vector_store,
)

__all__ = [
    "settings",
    "Settings",
    "get_settings",
    "get_retrieval_service",
    "get_vector_store",
]
