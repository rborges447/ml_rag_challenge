import chromadb
from chromadb.api.models.Collection import Collection


class VectorStore:
    def __init__(self, persist_directory: str = "data/chroma") -> None:
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection: Collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            documents.append(chunk["text"])
            metadatas.append(
                {
                    "page": chunk["page"],
                    "source": chunk["source"],
                }
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(self, query_embedding: list[float], n_results: int = 5) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )