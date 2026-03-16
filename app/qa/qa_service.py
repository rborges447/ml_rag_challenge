"""
Serviço de QA: montagem do prompt a partir da pergunta e dos chunks recuperados.
"""
from app.qa.prompt_builder import build_prompt as _build_prompt


class QAService:
    """Realiza o serviço de montar o prompt para o LLM (pergunta + contexto dos chunks)."""

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        """Retorna o prompt montado (pergunta + contexto dos chunks)."""
        return _build_prompt(question, chunks)
