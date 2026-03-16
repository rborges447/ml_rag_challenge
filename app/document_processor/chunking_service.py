"""
Divisão de documentos em chunks com RecursiveCharacterTextSplitter (LangChain).
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class ChunkingService:
    """Aplica splitting com chunk_size e chunk_overlap da config."""

    def __init__(self) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            # Valores default vêm de settings, mas aqui priorizamos capturar
            # blocos técnicos (tabelas/listas) de forma mais inteira.
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            # Removemos o separador por sentença (". ") porque ele tende a
            # quebrar linhas de tabela ou listas técnicas em pontos ruins.
            # Mantemos prioridade em quebras duplas/simples de linha e depois
            # espaço, deixando "" apenas como último recurso.
            separators=["\n\n", "\n", " ", ""],
        )

    def split(self, documents: list[Document]) -> list[Document]:
        """Retorna lista de chunks (Documents) a partir dos documentos por página."""
        return self._splitter.split_documents(documents)

