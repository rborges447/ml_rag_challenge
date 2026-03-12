"""
Config e dependências (settings, embedding, vector store).
"""
from app.core.config import settings, Settings
from app.core.dependencies import get_settings, get_embedding_function, get_vector_store

__all__ = [
    "settings",
    "Settings",
    "get_settings",
    "get_embedding_function",
    "get_vector_store",
]
