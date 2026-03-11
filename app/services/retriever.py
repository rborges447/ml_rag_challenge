from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


def _distance_to_score(distance: float) -> float:
    """Converte distância L2 em score (maior = mais similar)."""
    return 1.0 / (1.0 + distance)


class Retriever:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 8,
        max_distance: float | None = None,
    ) -> list[dict]:
        query_embedding = self.embedding_service.embed_query(question)

        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_chunks = []
        seen_texts = set()

        for doc, metadata, distance in zip(documents, metadatas, distances):
            if max_distance is not None and distance > max_distance:
                continue

            normalized_text = doc.strip() if doc else ""

            if not normalized_text:
                continue

            if normalized_text in seen_texts:
                continue

            seen_texts.add(normalized_text)

            score = _distance_to_score(distance)

            retrieved_chunks.append(
                {
                    "text": doc,
                    "page": metadata.get("page"),
                    "source": metadata.get("source"),
                    "distance": distance,
                    "score": score,
                }
            )

        return retrieved_chunks
