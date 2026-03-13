from __future__ import annotations

from dataclasses import dataclass

from app.clients.llm_client import LLMClient
from app.core.config import settings


TEST_PROMPT = (
    "Answer in one short line only. "
    "Say: integration test successful."
)


@dataclass
class CandidateResult:
    provider: str
    model: str
    success: bool
    used_by_llm_client: bool
    response_text: str | None = None
    error_message: str | None = None
    likely_would_work_with_paid_access: bool | None = None
    diagnosis: str | None = None


def classify_error_message(message: str) -> tuple[bool | None, str]:
    msg = message.lower()

    if any(term in msg for term in [
        "api key is not configured",
        "missing api key",
        "no api key",
    ]):
        return (
            False,
            "Falha de configuração local: chave ausente ou provider não configurado.",
        )

    if any(term in msg for term in [
        "quota",
        "billing",
        "insufficient_quota",
        "rate limit",
        "resource exhausted",
        "free tier",
        "not available for your current plan",
        "access to model",
        "does not have access",
        "429",
    ]):
        return (
            True,
            "A integração parece correta; o erro parece ser de quota, billing, plano ou acesso ao modelo.",
        )

    if any(term in msg for term in [
        "401",
        "403",
        "unauthorized",
        "authentication",
        "permission denied",
        "invalid api key",
    ]):
        return (
            None,
            "A chamada chegou ao provider, mas houve falha de autenticação/permissão.",
        )

    if any(term in msg for term in [
        "timeout",
        "timed out",
        "deadline exceeded",
        "service unavailable",
        "temporarily unavailable",
        "503",
    ]):
        return (
            None,
            "Erro transitório ou timeout. Pode funcionar em outra tentativa.",
        )

    return (
        None,
        "Erro não classificado automaticamente. Verifique a mensagem completa.",
    )


def test_llm_client_routing() -> None:
    """
    Testa o LLMClient com a rota configurada no .env.
    Esse é o teste mais importante, porque é o contrato usado pelo resto do app.
    """
    print("\n" + "=" * 80)
    print("TESTE 1 - LLMClient com fallback real")
    print("=" * 80)

    print("Rota configurada:")
    for idx, (provider, model) in enumerate(settings.llm_route_list, start=1):
        print(f"  {idx}. {provider}:{model}")

    client = LLMClient()

    try:
        response = client.generate(TEST_PROMPT)
        print("\nRESULTADO:")
        print("  success:   True")
        print(f"  provider:  {client.last_used_provider}")
        print(f"  model:     {client.last_used_model}")
        print(f"  response:  {response}")

    except Exception as exc:
        likely_paid, diagnosis = classify_error_message(str(exc))
        print("\nRESULTADO:")
        print("  success:   False")
        print(f"  error:     {exc}")
        print(f"  diagnosis: {diagnosis}")
        print(f"  likely_would_work_with_paid_access: {likely_paid}")


def test_llm_client_each_route_item() -> None:
    """
    Testa cada item da rota individualmente, mas ainda usando o LLMClient.
    Para isso, sobrescrevemos temporariamente a rota para um único candidate por vez.
    """
    print("\n" + "=" * 80)
    print("TESTE 2 - Cada modelo individualmente via LLMClient")
    print("=" * 80)

    original_route = settings.llm_route
    results: list[CandidateResult] = []

    try:
        for provider, model in settings.llm_route_list:
            single_route = f"{provider}:{model}"
            settings.llm_route = single_route

            print(f"\nTestando rota isolada: {single_route}")

            try:
                client = LLMClient()
                response = client.generate(TEST_PROMPT)

                result = CandidateResult(
                    provider=provider,
                    model=model,
                    success=True,
                    used_by_llm_client=True,
                    response_text=response,
                    diagnosis="Chamada concluída com sucesso via LLMClient.",
                )

            except Exception as exc:
                likely_paid, diagnosis = classify_error_message(str(exc))
                result = CandidateResult(
                    provider=provider,
                    model=model,
                    success=False,
                    used_by_llm_client=True,
                    error_message=str(exc),
                    likely_would_work_with_paid_access=likely_paid,
                    diagnosis=diagnosis,
                )

            results.append(result)

    finally:
        settings.llm_route = original_route

    print("\n" + "-" * 80)
    print("RESUMO")
    print("-" * 80)

    for result in results:
        print(f"\nModelo: {result.provider}:{result.model}")
        print(f"  success:   {result.success}")
        print(f"  via_llm_client: {result.used_by_llm_client}")

        if result.success:
            print("  status:    OK")
            print(f"  response:  {result.response_text}")
        else:
            print(f"  error:     {result.error_message}")
            print(f"  diagnosis: {result.diagnosis}")
            print(
                "  likely_would_work_with_paid_access: "
                f"{result.likely_would_work_with_paid_access}"
            )


if __name__ == "__main__":
    test_llm_client_routing()
    test_llm_client_each_route_item()