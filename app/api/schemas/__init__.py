"""
Schemas de request/response da API.
"""
from app.api.schemas.document import DocumentUploadResponse
from app.api.schemas.question import QuestionRequest, QuestionResponse

__all__ = [
    "DocumentUploadResponse",
    "QuestionRequest",
    "QuestionResponse",
]
