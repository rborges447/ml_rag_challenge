"""
Fachada Q&A: retrieval hoje; retrieval + LLM no futuro.
"""
from app.services.qa.qa_service import QAService, get_qa_service

__all__ = ["QAService", "get_qa_service"]
