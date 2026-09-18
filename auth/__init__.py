"""Authentication providers for the crawler platform."""

from .api_key import ApiKeyAuth
from .base import AuthError, AuthProvider
from .session_auth import SessionAuth


def provider_from_settings(settings):
    """Select the documented auth priority without exposing secret values."""

    mode = settings.auth_mode
    if mode in {"api_key", "auto"} and settings.api_key:
        return ApiKeyAuth(settings.api_key)
    if mode in {"session", "login", "auto"} and settings.email and settings.password:
        return SessionAuth(settings.email, settings.password, login_path=settings.login_path)
    if mode not in {"auto", "api_key", "session", "login"}:
        raise AuthError(f"AUTH_FAILED: unsupported auth mode '{mode}'")
    raise AuthError("AUTH_FAILED: configure CRAWLER_API_KEY or CRAWLER_EMAIL/CRAWLER_PASSWORD")


__all__ = ["ApiKeyAuth", "AuthError", "AuthProvider", "SessionAuth", "provider_from_settings"]
