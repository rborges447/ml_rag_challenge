from typing import List, Dict, Any


class DummyRetrievalService:
    """Versão mínima para garantir contrato básico de retrieve."""

    def __init__(self) -> None:
        self._dummy_chunks: List[Dict[str, Any]] = [
            {"text": "conteúdo 1", "source": "doc1", "page": 1, "score": 0.9},
            {"text": "conteúdo 2", "source": "doc2", "page": 2, "score": 0.8},
        ]

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        initial_k: int | None = None,
        max_distance: float | None = None,
        min_score: float | None = None,
    ) -> List[Dict[str, Any]]:
        chunks = self._dummy_chunks
        if top_k is not None:
            chunks = chunks[:top_k]
        return chunks


def test_dummy_retrieval_respects_top_k() -> None:
    service = DummyRetrievalService()
    chunks = service.retrieve("pergunta", top_k=1)
    assert len(chunks) == 1
    assert chunks[0]["source"] == "doc1"

