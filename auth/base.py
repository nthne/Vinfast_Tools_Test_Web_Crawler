"""Auth provider protocol and safe errors."""

from __future__ import annotations

from typing import Protocol

import httpx


class AuthError(RuntimeError):
    """Authentication failed or cannot be configured safely."""


class AuthProvider(Protocol):
    def authenticate(self, client: httpx.Client) -> None:
        """Mutate only the supplied client session."""
