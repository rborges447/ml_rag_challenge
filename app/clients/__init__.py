"""
Clientes externos (por exemplo, LLMs).

Interface pública deste pacote:
- LLMClient: fachada para provedores de LLM.
- Providers específicos ficam em app.clients.providers.
"""

from app.clients.llm_client import LLMClient

__all__ = [
    "LLMClient",
]
