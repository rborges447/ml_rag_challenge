from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider is configured and ready to use."""
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a text answer from the given prompt."""
        raise NotImplementedError