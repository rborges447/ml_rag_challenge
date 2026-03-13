from concurrent.futures import ThreadPoolExecutor, TimeoutError

from openai import OpenAI

from app.clients.providers.base import BaseLLMProvider
from app.core.config import settings


class OpenAIProvider(BaseLLMProvider):
    provider_name = "openai"

    def __init__(self, model: str) -> None:
        self.api_key = settings.openai_api_key
        self.model_name = model
        self.timeout_seconds = settings.llm_timeout_seconds
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    def _call_model(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            input=prompt,
        )

        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise RuntimeError("OpenAI returned an empty response.")

        return text.strip()

    def generate(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI API key is not configured.")

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._call_model, prompt)
                return future.result(timeout=self.timeout_seconds)

        except TimeoutError as exc:
            raise RuntimeError(
                f"OpenAI provider timeout after {self.timeout_seconds}s "
                f"(model={self.model_name})"
            ) from exc

        except Exception as exc:
            raise RuntimeError(
                f"OpenAI provider failed (model={self.model_name}): {exc}"
            ) from exc