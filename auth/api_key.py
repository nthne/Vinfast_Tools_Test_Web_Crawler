"""Bearer/x-token API-key authentication."""

from __future__ import annotations

import httpx


class ApiKeyAuth:
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise ValueError("api_key must not be empty")
        self._api_key = api_key.strip()

    def authenticate(self, client: httpx.Client) -> None:
        client.headers.update(
            {
                "Authorization": f"Bearer {self._api_key}",
                # The observed frontend sends both headers for authenticated API calls.
                "x-token": self._api_key,
            }
        )

    def __repr__(self) -> str:
        return "ApiKeyAuth(api_key='***')"
