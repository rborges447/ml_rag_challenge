import os

import pytest

from app.core.config import Settings


def test_settings_defaults_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings deve carregar valores padrão quando variáveis de ambiente são as esperadas."""
    monkeypatch.setenv("LLM_PROVIDERS", "gemini")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.0-flash")

    settings = Settings()

    assert settings.llm_providers == "gemini"
    assert settings.llm_provider_list == ["gemini"]
    assert settings.gemini_model == "gemini-2.0-flash"


def test_settings_overrides_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings deve respeitar variáveis de ambiente."""
    monkeypatch.setenv("LLM_PROVIDERS", "gemini, openai")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3-flash-preview")

    settings = Settings()

    assert settings.llm_providers == "gemini, openai"
    assert settings.llm_provider_list == ["gemini", "openai"]
    assert settings.gemini_model == "gemini-3-flash-preview"


def test_settings_ignores_extra_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """
    Settings deve ignorar chaves extras no .env graças a extra=\"ignore\".
    """
    env_file = tmp_path / ".env"
    env_file.write_text(
        "UNKNOWN_KEY=foo\n"
        "api_base_url=http://localhost:9999\n"
        "ui_http_timeout_seconds=123\n",
        encoding="utf-8",
    )

    from pydantic_settings import SettingsConfigDict

    class LocalSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=str(env_file),
            env_file_encoding="utf-8",
            extra="ignore",
        )

    settings = LocalSettings()

    assert isinstance(settings, LocalSettings)