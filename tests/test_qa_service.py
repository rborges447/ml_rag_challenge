from unittest.mock import MagicMock

from langchain_core.documents import Document

from app.pipelines import QuestionPipeline


class MockVectorStore:
    """Retorna chunks fixos para o teste."""

    def similarity_search_with_score_by_vector(
        self, query_embedding: list[float], k: int = 8
    ) -> list[tuple[Document, float]]:
        return [
            (Document(page_content="conteúdo 1", metadata={"source": "doc1.pdf", "page": 1}), 0.1),
            (Document(page_content="conteúdo 2", metadata={"source": "doc1.pdf", "page": 2}), 0.2),
            (Document(page_content="conteúdo 3", metadata={"source": "doc2.pdf", "page": 1}), 0.3),
        ][:k]


class MockLLMClient:
    """Retorna resposta fixa para o teste."""

    def generate(self, prompt: str) -> str:
        return "resposta gerada pela LLM"


def test_question_pipeline_returns_expected_structure() -> None:
    pipeline = QuestionPipeline(
        vector_store=MockVectorStore(),
        llm_client=MockLLMClient(),
    )

    result = pipeline.run("Pergunta de teste", top_k=2)

    assert "answer" in result
    assert "references" in result
    assert "retrieved_chunks" in result

    assert result["answer"] == "resposta gerada pela LLM"
    assert len(result["retrieved_chunks"]) == 2

    refs = result["references"]
    assert all("doc1.pdf - page" in ref or "doc2.pdf - page" in ref for ref in refs)
