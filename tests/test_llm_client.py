from typing import Any
from unittest.mock import patch

from app.clients import LLMClient


class DummyProvider:
    def __init__(self) -> None:
        self.last_prompt: str | None = None

    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, **_: Any) -> str:
        self.last_prompt = prompt
        return "dummy response"


def test_llm_client_uses_provider() -> None:
    dummy = DummyProvider()
    with patch.object(LLMClient, "__init__", lambda self: None):
        client = LLMClient()
        client.providers = [dummy]

    response = client.generate("pergunta de teste")

    assert response == "dummy response"
    assert dummy.last_prompt == "pergunta de teste"

