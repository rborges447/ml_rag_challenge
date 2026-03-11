"""
Orquestrador da ingestão: salva PDF, pré-processa texto, chunking configurável, metadados ricos, indexa no Chroma.
"""
import os
import re
import uuid

from fastapi import UploadFile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.services.pdf_text_utils import preprocess_pages
from app.services.vector_store import VectorStore


def _is_intro_page(page: int, text: str) -> bool:
    """Heurística: página introdutória (capa, sumário, introdução)."""
    if page <= getattr(settings, "intro_page_max", 2):
        return True
    lower = text.lower()[:1500]
    intro_markers = ("introdução", "introducao", "sumário", "sumario", "capítulo 1", "capitulo 1")
    if any(m in lower for m in intro_markers) and len(text.split()) < 200:
        return True
    return False


def _section_hint(chunk_text: str) -> str:
    """Inferir hint de seção: primeira linha curta que pareça título."""
    if not chunk_text or len(chunk_text) < 10:
        return ""
    first_line = chunk_text.split("\n")[0].strip()
    if len(first_line) > 60 or not first_line:
        return ""
    if re.match(r"^[\d\.\-\s]+\s*$", first_line):
        return ""
    return first_line[:100]


class DocumentIngestionService:
    def __init__(self, vector_store: VectorStore | None = None) -> None:
        self.upload_dir = "data/raw"
        self.vector_store = vector_store or get_vector_store()
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
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
        raw_documents = loader.load()

        source_name = file.filename or os.path.basename(file_path)
        pages_list = []
        for doc in raw_documents:
            p = doc.metadata.get("page", 0)
            page_num = p + 1 if isinstance(p, int) else p
            pages_list.append({"page": page_num, "text": doc.page_content or ""})

        pages_list = preprocess_pages(pages_list)

        documents_for_split = []
        for p in pages_list:
            page_num = p["page"]
            text = p["text"]
            if not text.strip():
                continue
            documents_for_split.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": source_name,
                        "page": page_num,
                    },
                )
            )

        chunks = self._text_splitter.split_documents(documents_for_split)

        for i, chunk in enumerate(chunks):
            text = chunk.page_content or ""
            meta = chunk.metadata or {}
            page = meta.get("page", 0)
            meta["chunk_id"] = str(uuid.uuid4())
            meta["chunk_index"] = i
            meta["char_count"] = len(text)
            meta["is_intro_page"] = _is_intro_page(page, text)
            meta["section_hint"] = _section_hint(text)
            chunk.metadata = meta

        self.vector_store.add_documents(chunks)

        return {
            "file_path": file_path,
            "total_chunks": len(chunks),
        }
