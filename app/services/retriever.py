from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class Retriever:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve(self, question: str, top_k: int = 8) -> list[dict]:
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
            normalized_text = doc.strip()

            if not normalized_text:
                continue

            if normalized_text in seen_texts:
                continue

            seen_texts.add(normalized_text)

            retrieved_chunks.append(
                {
                    "text": doc,
                    "page": metadata.get("page"),
                    "source": metadata.get("source"),
                    "distance": distance,
                }
            )

        return retrieved_chunks