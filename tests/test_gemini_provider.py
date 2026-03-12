from app.clients.providers import GeminiProvider
from app.core.config import settings


def main() -> None:
    print("gemini model:", settings.gemini_model)
    print("timeout:", settings.llm_timeout_seconds)

    provider = GeminiProvider()

    print("available:", provider.is_available())

    if not provider.is_available():
        print("Gemini is not configured.")
        return

    prompt = "Explique em uma frase o que é um motor elétrico."

    try:
        response = provider.generate(prompt)
        print("response:")
        print(response)
    except Exception as exc:
        print("error:")
        print(type(exc).__name__)
        print(exc)


if __name__ == "__main__":
    main()