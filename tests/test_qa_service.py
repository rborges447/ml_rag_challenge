from typing import Any

from app.use_cases.answer_question import AnswerQuestionUseCase


class MockRetrievalPipeline:
    """Retorna chunks fixos para o teste."""

    def run(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        chunks = [
            {"text": "conteúdo 1", "source": "doc1.pdf", "page": 1},
            {"text": "conteúdo 2", "source": "doc1.pdf", "page": 2},
            {"text": "conteúdo 3", "source": "doc2.pdf", "page": 1},
        ]
        if top_k is not None:
            chunks = chunks[:top_k]
        return chunks


class MockGenerationPipeline:
    """Retorna resposta fixa para o teste."""

    def run(self, question: str, chunks: list[dict]) -> str:
        return "resposta gerada pela LLM"


def test_answer_question_use_case_returns_expected_structure() -> None:
    use_case = AnswerQuestionUseCase(
        retrieval_pipeline=MockRetrievalPipeline(),
        generation_pipeline=MockGenerationPipeline(),
    )

    result = use_case.run("Pergunta de teste", top_k=2)

    assert "answer" in result
    assert "references" in result
    assert "retrieved_chunks" in result

    assert result["answer"] == "resposta gerada pela LLM"
    assert len(result["retrieved_chunks"]) == 2

    refs = result["references"]
    assert all("doc1.pdf - page" in ref or "doc2.pdf - page" in ref for ref in refs)
