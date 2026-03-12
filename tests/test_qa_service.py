from typing import Any, Dict, List

from app.services.qa.qa_service import QAService


class DummyQAService(QAService):
    def __init__(self) -> None:
        # Não chama super().__init__ para evitar dependências reais
        self._retrieved: List[Dict[str, Any]] = [
            {"text": "conteúdo 1", "source": "doc1.pdf", "page": 1},
            {"text": "conteúdo 2", "source": "doc1.pdf", "page": 2},
            {"text": "conteúdo 3", "source": "doc2.pdf", "page": 1},
        ]

        class DummyLLM:
            def generate(self, prompt: str) -> str:
                return "resposta gerada pela LLM"

        self._llm = DummyLLM()

    def retrieve(  # type: ignore[override]
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> List[Dict[str, Any]]:
        chunks = self._retrieved
        if top_k is not None:
            chunks = chunks[:top_k]
        return chunks


def test_qa_service_answer_returns_expected_structure() -> None:
    service = DummyQAService()

    result = service.answer("Pergunta de teste", top_k=2)

    assert "answer" in result
    assert "references" in result
    assert "retrieved_chunks" in result

    assert result["answer"] == "resposta gerada pela LLM"
    assert len(result["retrieved_chunks"]) == 2

    # Referências devem ser únicas e baseadas em source/page
    refs = result["references"]
    assert all("doc1.pdf - page" in ref or "doc2.pdf - page" in ref for ref in refs)
