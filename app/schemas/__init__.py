"""
Schemas de request/response da API.
"""
from app.schemas.document import DocumentUploadResponse
from app.schemas.question import QuestionRequest, QuestionResponse

__all__ = [
    "DocumentUploadResponse",
    "QuestionRequest",
    "QuestionResponse",
]
