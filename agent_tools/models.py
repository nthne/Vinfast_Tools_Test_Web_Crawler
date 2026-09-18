"""Shared result models for agent tools."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


_SECRET_KEYS = {"password", "token", "refresh_token", "cookie", "api_key", "authorization"}


def _sanitize(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in _SECRET_KEYS:
        return "***"
    if isinstance(value, dict):
        return {str(k): _sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize(item) for item in value]
    return value


@dataclass
class ToolResult:
    """A safe, explainable result returned by an agent tool."""

    tool_name: str
    answer: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    confidence: str = "observed"
    classification: str | None = None
    read_only: bool = True
    new_tool_proposal: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return _sanitize(asdict(self))
