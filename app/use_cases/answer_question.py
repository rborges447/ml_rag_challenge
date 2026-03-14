"""
Use case: responder pergunta (retrieval → generation → resposta com referências).
"""
from app.services.pipelines import GenerationPipeline, RetrievalPipeline


class AnswerQuestionUseCase:
    """Executa retrieval e generation e devolve resposta com referências e chunks."""

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline | None = None,
        generation_pipeline: GenerationPipeline | None = None,
    ) -> None:
        self._retrieval_pipeline = retrieval_pipeline or RetrievalPipeline()
        self._generation_pipeline = generation_pipeline or GenerationPipeline()

    def run(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> dict:
        """
        Retorna {"answer": str, "references": list[str], "retrieved_chunks": list[dict]}.
        """
        retrieved_chunks = self._retrieval_pipeline.run(
            question=question,
            top_k=top_k,
            initial_k=initial_k,
            max_distance=max_distance,
            min_score=min_score,
        )

        answer = self._generation_pipeline.run(question=question, chunks=retrieved_chunks)

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
        }
