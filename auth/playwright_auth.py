"""Optional browser-auth boundary for JS/SSO systems.

The MVP intentionally does not automate CAPTCHA or type credentials into a browser.
This boundary lets a future Playwright integration supply an already-authenticated
storage state without coupling the QA rules to browser automation.
"""

from __future__ import annotations

from pathlib import Path

from .base import AuthError


class PlaywrightAuth:
    def __init__(self, storage_state_path: str | None = None):
        self.storage_state_path = storage_state_path

    def authenticate(self, client) -> None:
        if self.storage_state_path and Path(self.storage_state_path).exists():
            raise AuthError(
                "AUTH_FAILED: Playwright storage state requires a browser-backed client; "
                "use the optional browser adapter"
            )
        raise AuthError("AUTH_FAILED: browser/SSO authentication is not configured")

    def __repr__(self) -> str:
        return f"PlaywrightAuth(storage_state_path={self.storage_state_path!r})"
