from concurrent.futures import ThreadPoolExecutor, TimeoutError

from google import genai

from app.clients.providers.base import BaseLLMProvider
from app.core.config import settings


class GeminiProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.timeout_seconds = settings.llm_timeout_seconds
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    def _call_model(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = getattr(response, "text", None)
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")

        return text.strip()

    def generate(self, prompt: str) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini API key is not configured.")

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._call_model, prompt)
                return future.result(timeout=self.timeout_seconds)

        except TimeoutError as exc:
            raise RuntimeError(
                f"Gemini provider timeout after {self.timeout_seconds}s"
            ) from exc

        except Exception as exc:
            raise RuntimeError(f"Gemini provider failed: {exc}") from exc