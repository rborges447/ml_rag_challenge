from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.clients.providers.gemini_provider import GeminiProvider
from app.clients.providers.openai_provider import OpenAIProvider


TEST_PROMPT = (
    "Answer with exactly this format: "
    "'OK | provider=<provider> | model=<model> | summary=test successful'. "
    "Do not add anything else."
)


@dataclass
class CandidateResult:
    provider: str
    model: str
    available: bool
    success: bool
    response_text: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    likely_would_work_with_paid_access: bool | None = None
    diagnosis: str | None = None


def classify_error(exc: Exception) -> tuple[str, bool | None, str]:
    """
    Classifica erros de forma heurística.
    Não garante 100%, mas ajuda bastante no diagnóstico.
    """
    msg = str(exc).lower()

    # Configuração local / chave ausente
    if any(term in msg for term in [
        "api key is not configured",
        "api_key",
        "no api key",
        "missing api key",
    ]):
        return (
            "missing_configuration",
            False,
            "Chave de API ausente ou provider não configurado localmente.",
        )

    # Autenticação
    if any(term in msg for term in [
        "invalid api key",
        "incorrect api key",
        "authentication",
        "unauthorized",
        "permission denied",
        "401",
        "403",
    ]):
        return (
            "authentication_or_permission",
            None,
            "A requisição chegou ao provider, mas houve falha de autenticação/permissão.",
        )

    # Quota / billing / plano / limite
    if any(term in msg for term in [
        "quota",
        "rate limit",
        "billing",
        "insufficient_quota",
        "exceeded your current quota",
        "429",
        "resource exhausted",
        "free tier",
        "not available for your current plan",
        "model not found",
        "access to model",
        "does not have access",
    ]):
        return (
            "quota_or_plan_or_model_access",
            True,
            "A integração parece correta; o problema parece ser quota, plano ou acesso ao modelo.",
        )

    # Timeout / indisponibilidade temporária
    if any(term in msg for term in [
        "timeout",
        "timed out",
        "deadline exceeded",
        "temporarily unavailable",
        "service unavailable",
        "503",
    ]):
        return (
            "transient_provider_error",
            None,
            "Erro transitório do provider ou timeout. A configuração pode estar correta.",
        )

    return (
        "unknown_error",
        None,
        "Erro não classificado automaticamente. Verifique a mensagem completa.",
    )


def build_candidate(provider_name: str, model_name: str):
    if provider_name == "gemini":
        return GeminiProvider(model=model_name)

    if provider_name == "openai":
        return OpenAIProvider(model=model_name)

    raise ValueError(f"Unsupported provider in LLM route: {provider_name}")


def get_route_candidates() -> list[tuple[str, str]]:
    """
    Espera que exista settings.llm_route_list no formato:
    [("gemini", "gemini-3-flash"), ("openai", "gpt-4.1-mini")]
    """
    return settings.llm_route_list


def run_single_candidate(provider_name: str, model_name: str) -> CandidateResult:
    provider = build_candidate(provider_name, model_name)

    if not provider.is_available():
        return CandidateResult(
            provider=provider_name,
            model=model_name,
            available=False,
            success=False,
            error_type="provider_unavailable",
            error_message="Provider is not available with current local configuration.",
            likely_would_work_with_paid_access=False,
            diagnosis="Provider indisponível localmente. Normalmente isso significa chave ausente ou config incompleta.",
        )

    try:
        text = provider.generate(TEST_PROMPT)
        return CandidateResult(
            provider=provider_name,
            model=model_name,
            available=True,
            success=True,
            response_text=text,
            diagnosis="Chamada concluída com sucesso.",
        )
    except Exception as exc:
        error_type, likely_paid, diagnosis = classify_error(exc)
        return CandidateResult(
            provider=provider_name,
            model=model_name,
            available=True,
            success=False,
            error_type=error_type,
            error_message=str(exc),
            likely_would_work_with_paid_access=likely_paid,
            diagnosis=diagnosis,
        )


def test_routing_mechanism() -> None:
    """
    Testa a rota inteira na ordem do fallback e mostra qual modelo respondeu primeiro.
    """
    print("\n" + "=" * 80)
    print("TESTE 1 - FALLBACK / ROUTING")
    print("=" * 80)

    candidates = get_route_candidates()
    print("Rota configurada:")
    for idx, (provider, model) in enumerate(candidates, start=1):
        print(f"  {idx}. {provider}:{model}")

    winner: CandidateResult | None = None
    all_results: list[CandidateResult] = []

    for provider_name, model_name in candidates:
        result = run_single_candidate(provider_name, model_name)
        all_results.append(result)

        print(f"\nTentativa -> {provider_name}:{model_name}")
        print(f"  available: {result.available}")
        print(f"  success:   {result.success}")

        if result.success:
            print(f"  response:  {result.response_text}")
            winner = result
            break

        print(f"  error_type: {result.error_type}")
        print(f"  diagnosis:  {result.diagnosis}")
        if result.error_message:
            print(f"  error:      {result.error_message}")

    print("\n" + "-" * 80)
    if winner:
        print("RESULTADO FINAL DO ROUTING:")
        print(f"  SUCESSO com {winner.provider}:{winner.model}")
    else:
        print("RESULTADO FINAL DO ROUTING:")
        print("  Nenhum candidate respondeu com sucesso.")
    print("-" * 80)


def test_each_model_individually() -> None:
    """
    Testa todos os modelos individualmente, mesmo que o primeiro já tenha funcionado.
    """
    print("\n" + "=" * 80)
    print("TESTE 2 - TESTE INDIVIDUAL DE CADA MODELO")
    print("=" * 80)

    candidates = get_route_candidates()
    results: list[CandidateResult] = []

    for provider_name, model_name in candidates:
        result = run_single_candidate(provider_name, model_name)
        results.append(result)

    for result in results:
        print(f"\nModelo: {result.provider}:{result.model}")
        print(f"  available: {result.available}")
        print(f"  success:   {result.success}")

        if result.success:
            print("  status:    OK")
            print(f"  response:  {result.response_text}")
            continue

        print(f"  error_type: {result.error_type}")
        print(f"  diagnosis:  {result.diagnosis}")
        print(
            "  likely_would_work_with_paid_access: "
            f"{result.likely_would_work_with_paid_access}"
        )
        if result.error_message:
            print(f"  error:      {result.error_message}")

    print("\n" + "-" * 80)
    print("RESUMO")
    for result in results:
        if result.success:
            status = "OK"
        else:
            status = f"FAIL ({result.error_type})"

        print(f"  - {result.provider}:{result.model} -> {status}")
    print("-" * 80)


if __name__ == "__main__":
    test_routing_mechanism()
    test_each_model_individually()