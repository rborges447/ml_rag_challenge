from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.services.vector_store import VectorStore


class FakeEmbeddings(Embeddings):
    """Embedding fake para testes (evita baixar modelo real)."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1] * 384


def test_vector_store_add_and_search(tmp_path: Path) -> None:
    base_path = Path(tmp_path)

    vs = VectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(base_path),
        collection_name="test_collection",
    )

    documents = [
        Document(page_content="Primeiro documento de teste", metadata={"source": "doc1", "page": 1}),
        Document(page_content="Segundo documento de teste", metadata={"source": "doc2", "page": 2}),
    ]

    ids = vs.add_documents(documents)
    assert len(ids) == 2

    results = vs.similarity_search_with_score("documento", k=2)
    assert len(results) == 2
    for doc, score in results:
        assert hasattr(doc, "page_content")
        assert hasattr(doc, "metadata")

