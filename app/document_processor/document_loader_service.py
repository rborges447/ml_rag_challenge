"""
Carrega PDF de forma table-aware: extrai tabelas (cabeçalho + linhas) como blocos únicos
e texto narrativo por página, para preservar estrutura no RAG.
"""
from app.document_processor.table_aware_loader import load_table_aware


class DocumentLoaderService:
    """Carrega PDF e retorna list[{"page": int (1-indexed), "text": str, "is_table": bool}]."""

    def load(self, file_path: str, source_name: str) -> list[dict]:
        """
        Carrega o PDF em file_path e retorna lista de blocos com page (1-indexed), text e is_table.
        Blocos com is_table=True vêm de find_tables() (cabeçalho + linhas em um único texto).
        """
        return load_table_aware(file_path, source_name)

