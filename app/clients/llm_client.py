from app.core.config import settings
from app.clients.providers.gemini_provider import GeminiProvider


class LLMClient:
    def __init__(self):
        self.providers = []

        if "gemini" in settings.llm_provider_list:
            self.providers.append(GeminiProvider())

    def generate(self, prompt: str) -> str:
        last_error = None

        for provider in self.providers:
            if not provider.is_available():
                continue

            try:
                return provider.generate(prompt)

            except Exception as exc:
                last_error = exc
                print(f"Provider {provider.__class__.__name__} failed:", exc)

        raise RuntimeError(f"All LLM providers failed: {last_error}")