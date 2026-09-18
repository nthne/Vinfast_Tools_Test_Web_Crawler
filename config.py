"""Environment-only application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during minimal installs
    load_dotenv = None


def _optional_str(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class AppSettings:
    """Runtime configuration with secrets hidden from repr/log output."""

    base_url: str | None = None
    email: str | None = None
    password: str | None = None
    api_key: str | None = None
    auth_mode: str = "auto"
    data_path: str | None = None
    db_path: str = "artifacts/qa.sqlite3"
    max_concurrency: int = 10
    request_timeout: float = 30.0
    retry_count: int = 3
    login_path: str | None = None
    sources_path: str | None = None
    jobs_path: str | None = None
    pages_path: str | None = None
    page_detail_path: str | None = None
    page_view_path: str | None = None
    page_clean_preview_path: str | None = None
    clean_modes_path: str | None = None
    exports_path: str | None = None
    auth_storage_path: str = "artifacts/auth/storage_state.json"

    @classmethod
    def from_env(cls, *, load_dotenv_file: bool = True) -> "AppSettings":
        """Load `.env` if available, then read all settings from the process."""

        if load_dotenv_file and load_dotenv is not None:
            load_dotenv(override=False)
        return cls(
            base_url=_optional_str("CRAWLER_BASE_URL"),
            email=_optional_str("CRAWLER_EMAIL"),
            password=_optional_str("CRAWLER_PASSWORD"),
            api_key=_optional_str("CRAWLER_API_KEY"),
            auth_mode=(_optional_str("CRAWLER_AUTH_MODE") or "auto").lower(),
            data_path=_optional_str("CRAWLER_DATA_PATH"),
            db_path=_optional_str("QA_DB_PATH") or "artifacts/qa.sqlite3",
            max_concurrency=max(1, _int_env("QA_MAX_CONCURRENCY", 10)),
            request_timeout=max(1.0, _float_env("QA_REQUEST_TIMEOUT", 30.0)),
            retry_count=max(0, _int_env("QA_RETRY_COUNT", 3)),
            login_path=_optional_str("CRAWLER_LOGIN_PATH"),
            sources_path=_optional_str("CRAWLER_SOURCES_PATH"),
            jobs_path=_optional_str("CRAWLER_JOBS_PATH"),
            pages_path=_optional_str("CRAWLER_PAGES_PATH"),
            page_detail_path=_optional_str("CRAWLER_PAGE_DETAIL_PATH"),
            page_view_path=_optional_str("CRAWLER_PAGE_VIEW_PATH"),
            page_clean_preview_path=_optional_str("CRAWLER_PAGE_CLEAN_PREVIEW_PATH"),
            clean_modes_path=_optional_str("CRAWLER_CLEAN_MODES_PATH"),
            exports_path=_optional_str("CRAWLER_EXPORTS_PATH"),
            auth_storage_path=_optional_str("CRAWLER_AUTH_STORAGE_PATH")
            or "artifacts/auth/storage_state.json",
        )

    def ensure_runtime_dirs(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.auth_storage_path).parent.mkdir(parents=True, exist_ok=True)

    def safe_dict(self) -> dict[str, Any]:
        """Return config suitable for diagnostics with secrets redacted."""

        result = dict(self.__dict__)
        for key in ("password", "api_key"):
            if result.get(key):
                result[key] = "***"
        return result

    def __repr__(self) -> str:
        fields = ", ".join(f"{key}={value!r}" for key, value in self.safe_dict().items())
        return f"AppSettings({fields})"
