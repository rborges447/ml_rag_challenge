"""
Orquestrador da ingestão: salva PDF, carrega com LangChain, faz split e indexa no Chroma.
"""
import os
import uuid

from fastapi import UploadFile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.vector_store import VectorStore


class DocumentIngestionService:
    def __init__(self) -> None:
        self.upload_dir = "data/raw"
        self.vector_store = VectorStore()
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def process_uploaded_file(self, file: UploadFile) -> dict:
        os.makedirs(self.upload_dir, exist_ok=True)

        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{file_id}.pdf")

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        loader = PyMuPDFLoader(file_path)
        documents = loader.load()

        source_name = file.filename or os.path.basename(file_path)
        for doc in documents:
            doc.metadata["source"] = source_name
            # PyMuPDFLoader retorna page 0-indexed; normalizar para 1-indexed
            p = doc.metadata.get("page", 0)
            doc.metadata["page"] = p + 1 if isinstance(p, int) else p

        chunks = self._text_splitter.split_documents(documents)
        self.vector_store.add_documents(chunks)

        return {
            "file_path": file_path,
            "total_chunks": len(chunks),
        }
