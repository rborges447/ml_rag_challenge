"""
Pipeline de pergunta: RetrievalService (embed, search, filter, dedup, rerank) → QAService (prompt) → LLMClient → references.
"""
from app.clients import LLMClient
from app.core.config import settings
from app.core.dependencies import get_llm_client, get_qa_service, get_retrieval_service
from app.core.log_decorators import log_question_run
from app.qa import QAService
from app.retrieval import RetrievalService


class QuestionPipeline:
    """Orquestra o fluxo completo da pergunta: retrieval + geração + montagem de referências."""

    def __init__(
        self,
        retrieval_service: RetrievalService | None = None,
        qa_service: QAService | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self._retrieval_service = retrieval_service or get_retrieval_service()
        self._qa_service = qa_service or get_qa_service()
        self._llm_client = llm_client or get_llm_client()

    @log_question_run
    def run(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
        request_id: str | None = None,
    ) -> dict:
        """
        Retorna {"answer": str, "references": list[str], "retrieved_chunks": list[dict]}.
        """
        initial_k = initial_k if initial_k is not None else settings.retrieval_initial_k
        top_k = top_k if top_k is not None else settings.retrieval_top_k_final
        max_distance = max_distance if max_distance is not None else settings.retrieval_max_distance
        min_score = min_score if min_score is not None else settings.retrieval_min_score

        retrieved_chunks = self._retrieval_service.retrieve(
            question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            min_score=min_score,
        )

        prompt = self._qa_service.build_prompt(question, retrieved_chunks)
        answer = self._llm_client.generate(prompt)

        references_set: set[str] = set()
        for chunk in retrieved_chunks:
            source = chunk.get("source")
            page = chunk.get("page")
            if source is not None and page is not None:
                references_set.add(f"{source} - page {page}")
        references = sorted(references_set)

        return {
            "answer": answer,
            "references": references,
            "retrieved_chunks": retrieved_chunks,
            "_log": {
                "retrieved": len(retrieved_chunks),
                "references": len(references),
            },
        }
