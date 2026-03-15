from app.clients.providers.gemini_provider import GeminiProvider
from app.clients.providers.openai_provider import OpenAIProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


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
            if last_error is not None:
                logger.info(
                    "Executando fallback para provider %s:%s",
                    provider.provider_name,
                    provider.model_name,
                )
            if not provider.is_available():
                logger.warning(
                    "Skipping unavailable provider %s:%s",
                    provider.provider_name,
                    provider.model_name,
                )
                continue

            try:
                logger.info(
                    "Tentando provider LLM: %s:%s",
                    provider.provider_name,
                    provider.model_name,
                )
                response = provider.generate(prompt)
                self.last_used_provider = provider.provider_name
                self.last_used_model = provider.model_name
                logger.info(
                    "Resposta gerada com sucesso pelo provider %s:%s",
                    self.last_used_provider,
                    self.last_used_model,
                )
                return response

            except Exception as exc:
                last_error = exc
                logger.exception(
                    "Falha no provider %s:%s: %s",
                    provider.provider_name,
                    provider.model_name,
                    exc,
                )

        logger.error("Todos os providers LLM falharam")
        raise RuntimeError(f"All LLM providers failed: {last_error}")