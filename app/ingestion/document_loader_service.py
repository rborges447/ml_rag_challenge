"""
Carrega PDF com LangChain (PyMuPDFLoader) e retorna páginas em formato utilizável pelo pipeline.
"""
from langchain_community.document_loaders import PyMuPDFLoader


class DocumentLoaderService:
    """Carrega PDF e retorna list[{"page": int (1-indexed), "text": str}]."""

    def load(self, file_path: str, source_name: str) -> list[dict]:
        """
        Carrega o PDF em file_path e retorna lista de dicts com page (1-indexed) e text.
        source_name é preservado para uso posterior (ex.: metadados).
        """
        loader = PyMuPDFLoader(file_path)
        raw_documents = loader.load()
        pages_list = []
        for doc in raw_documents:
            p = doc.metadata.get("page", 0)
            page_num = p + 1 if isinstance(p, int) else p
            pages_list.append({
                "page": page_num,
                "text": doc.page_content or "",
            })
        return pages_list
