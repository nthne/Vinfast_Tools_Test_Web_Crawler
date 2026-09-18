"""Email/password login that retains the HTTP session and bearer token."""

from __future__ import annotations

from typing import Any

import httpx

from .base import AuthError


def _safe_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if isinstance(payload, dict):
        for key in ("detail", "message", "error"):
            if payload.get(key):
                return str(payload[key])
        nested = payload.get("data")
        if isinstance(nested, dict) and nested.get("message"):
            return str(nested["message"])
    return f"HTTP {response.status_code}"


class SessionAuth:
    DEFAULT_LOGIN_PATH = "/api-non/v1.0/users/login"

    def __init__(self, email: str, password: str, login_path: str | None = None):
        self._email = email
        self._password = password
        self.login_path = login_path or self.DEFAULT_LOGIN_PATH

    def authenticate(self, client: httpx.Client) -> None:
        try:
            response = client.post(
                self.login_path,
                json={"email": self._email, "password": self._password},
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
        except httpx.HTTPError as exc:
            raise AuthError(f"AUTH_FAILED: login request failed ({exc.__class__.__name__})") from exc
        if response.status_code < 200 or response.status_code >= 300:
            raise AuthError(f"AUTH_FAILED: {_safe_error(response)}")
        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise AuthError("AUTH_FAILED: login response was not JSON") from exc
        data = payload.get("data", payload) if isinstance(payload, dict) else payload
        if isinstance(payload, dict) and payload.get("status") not in (None, "success"):
            raise AuthError(f"AUTH_FAILED: {payload.get('message') or payload.get('error') or 'login rejected'}")
        if not isinstance(data, dict) or not data.get("token"):
            raise AuthError("AUTH_FAILED: login response did not contain a token")
        token_type = str(data.get("token_type") or "Bearer")
        token = str(data["token"])
        client.headers.update({"Authorization": f"{token_type} {token}", "x-token": token})

    def __repr__(self) -> str:
        return f"SessionAuth(email={self._email!r}, password='***', login_path={self.login_path!r})"
