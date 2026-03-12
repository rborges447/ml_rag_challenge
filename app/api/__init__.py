"""
Rotas da API.
"""
from app.api.routes_documents import router as documents_router
from app.api.routes_questions import router as questions_router

__all__ = ["documents_router", "questions_router"]
