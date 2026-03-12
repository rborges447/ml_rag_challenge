"""
Fachada para Q&A.
"""

from app.services.retrieval import RetrievalService
from app.services.qa.prompt_builder import build_prompt
from app.clients.llm_client import LLMClient


def get_qa_service() -> "QAService":
    return QAService()


class QAService:

    def __init__(self) -> None:
        self._retrieval = RetrievalService()
        self._llm = LLMClient()

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> list[dict]:
        return self._retrieval.retrieve(
            question=question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            min_score=min_score,
        )

    def answer(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> dict:
        retrieved_chunks = self.retrieve(
            question=question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            min_score=min_score,
        )

        prompt = build_prompt(question, retrieved_chunks)
        answer = self._llm.generate(prompt)

        references_set: set[str] = set()
        for chunk in retrieved_chunks:
            source = chunk.get("source")
            page = chunk.get("page")
            if not source or page is None:
                continue
            references_set.add(f"{source} - page {page}")

        references = sorted(references_set)

        return {
            "answer": answer,
            "references": references,
            "retrieved_chunks": retrieved_chunks,
        }
