"""
Pipeline 3 — Geração: question + chunks → prompt builder → LLM client → resposta.
"""
from app.clients import LLMClient
from app.services.qa.prompt_builder import build_prompt


class GenerationPipeline:
    """Orquestra o fluxo de geração: contexto (chunks) + pergunta → prompt → LLM → resposta."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client or LLMClient()

    def run(self, question: str, chunks: list[dict]) -> str:
        """Monta o prompt com os chunks e gera a resposta via LLM. Retorna o texto da resposta."""
        prompt = build_prompt(question, chunks)
        return self._llm_client.generate(prompt)
