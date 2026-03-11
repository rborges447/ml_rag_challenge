"""
Fachada para Q&A. Hoje apenas delega retrieval; no futuro: retrieval + geração (LLM).
Não integrar LLM ainda.
"""
from app.services.retrieval_service import RetrievalService


def get_qa_service() -> "QAService":
    return QAService()


class QAService:
    """Futuro: aqui entrará retrieval + geração (LLM). Por ora apenas retrieval."""

    def __init__(self) -> None:
        self._retrieval = RetrievalService()

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> list[dict]:
        """Delega para RetrievalService.retrieve()."""
        return self._retrieval.retrieve(
            question=question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            min_score=min_score,
        )
