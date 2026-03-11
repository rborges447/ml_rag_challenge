import os
import uuid

from fastapi import UploadFile

from app.services.embedding_service import EmbeddingService
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_chunker import chunk_text
from app.services.vector_store import VectorStore


class DocumentIngestionService:
    def __init__(self) -> None:
        self.upload_dir = "data/raw"
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    async def process_uploaded_file(self, file: UploadFile) -> dict:
        os.makedirs(self.upload_dir, exist_ok=True)

        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{file_id}.pdf")

        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        pages = extract_text_from_pdf(file_path)
        chunks = chunk_text(pages=pages, source=file.filename)

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        self.vector_store.add_chunks(chunks=chunks, embeddings=embeddings)

        return {
            "file_path": file_path,
            "total_chunks": len(chunks),
        }