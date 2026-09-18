import os

from config import AppSettings


def test_settings_use_safe_defaults_without_credentials(monkeypatch):
    for key in (
        "CRAWLER_BASE_URL",
        "CRAWLER_EMAIL",
        "CRAWLER_PASSWORD",
        "CRAWLER_API_KEY",
        "CRAWLER_AUTH_MODE",
        "CRAWLER_DATA_PATH",
    ):
        monkeypatch.delenv(key, raising=False)

    settings = AppSettings.from_env(load_dotenv_file=False)

    assert settings.base_url is None
    assert settings.email is None
    assert settings.password is None
    assert settings.api_key is None
    assert settings.auth_mode == "auto"
    assert settings.max_concurrency == 10
    assert settings.request_timeout == 30.0
    assert settings.retry_count == 3


def test_settings_read_environment_overrides(monkeypatch):
    monkeypatch.setenv("CRAWLER_BASE_URL", "https://crawler.internal")
    monkeypatch.setenv("CRAWLER_EMAIL", "qa@example.test")
    monkeypatch.setenv("CRAWLER_PASSWORD", "secret-from-env")
    monkeypatch.setenv("CRAWLER_API_KEY", "bearer-token")
    monkeypatch.setenv("CRAWLER_AUTH_MODE", "api_key")
    monkeypatch.setenv("QA_MAX_CONCURRENCY", "4")
    monkeypatch.setenv("QA_REQUEST_TIMEOUT", "12.5")
    monkeypatch.setenv("QA_RETRY_COUNT", "1")

    settings = AppSettings.from_env()

    assert settings.base_url == "https://crawler.internal"
    assert settings.email == "qa@example.test"
    assert settings.password == "secret-from-env"
    assert settings.api_key == "bearer-token"
    assert settings.auth_mode == "api_key"
    assert settings.max_concurrency == 4
    assert settings.request_timeout == 12.5
    assert settings.retry_count == 1


def test_settings_repr_never_exposes_secrets(monkeypatch):
    monkeypatch.setenv("CRAWLER_PASSWORD", "do-not-print")
    monkeypatch.setenv("CRAWLER_API_KEY", "also-do-not-print")

    rendered = repr(AppSettings.from_env())

    assert "do-not-print" not in rendered
    assert "also-do-not-print" not in rendered
    assert "***" in rendered
