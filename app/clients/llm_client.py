import logging

from app.core.config import settings
from app.clients.providers.gemini_provider import GeminiProvider
from app.clients.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.providers = []
        self.last_used_provider = None
        self.last_used_model = None

        for provider_name, model_name in settings.llm_route_list:
            provider = self._build_provider(provider_name, model_name)
            if provider is not None:
                self.providers.append(provider)

        if not self.providers:
            raise RuntimeError("No LLM providers were configured successfully.")

    def _build_provider(self, provider_name: str, model_name: str):
        if provider_name == "gemini":
            return GeminiProvider(model=model_name)

        if provider_name == "openai":
            return OpenAIProvider(model=model_name)

        logger.warning(
            "Ignoring unsupported LLM provider in route: %s:%s",
            provider_name,
            model_name,
        )
        return None

    def generate(self, prompt: str) -> str:
        self.last_used_provider = None
        self.last_used_model = None
        last_error = None

        for provider in self.providers:
            if not provider.is_available():
                logger.warning(
                    "Skipping unavailable provider %s:%s",
                    provider.provider_name,
                    provider.model_name,
                )
                continue

            try:
                logger.info(
                    "Trying provider %s:%s",
                    provider.provider_name,
                    provider.model_name,
                )
                response = provider.generate(prompt)

                self.last_used_provider = provider.provider_name
                self.last_used_model = provider.model_name

                logger.info(
                    "Success with provider %s:%s",
                    self.last_used_provider,
                    self.last_used_model,
                )
                return response

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Provider %s:%s failed: %s",
                    provider.provider_name,
                    provider.model_name,
                    exc,
                )

        raise RuntimeError(f"All LLM providers failed: {last_error}")