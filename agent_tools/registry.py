"""Registry and fallback proposal behavior for crawler agent tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .models import ToolResult


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    handler: Callable[..., ToolResult]


class ToolRegistry:
    """Register and invoke read-only tools by stable capability name."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, name: str, description: str, handler: Callable[..., ToolResult]) -> None:
        if not name.strip():
            raise ValueError("tool name must not be empty")
        self._tools[name] = ToolDefinition(name, description, handler)

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": definition.name, "description": definition.description}
            for definition in self._tools.values()
        ]

    def run(self, name: str, **kwargs: Any) -> ToolResult:
        try:
            definition = self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown crawler tool: {name}") from exc
        result = definition.handler(**kwargs)
        if not isinstance(result, ToolResult):
            raise TypeError(f"Tool {name} must return ToolResult")
        return result

    def propose(self, question: str, reason: str) -> ToolResult:
        return ToolResult(
            tool_name="tool_proposal",
            answer="No registered tool fully covers this question; proposal created for approval.",
            evidence=[{"field": "question", "observed": question}],
            confidence="inferred",
            new_tool_proposal={
                "question": question,
                "reason": reason,
                "suggested_name": "new_crawler_diagnostic",
                "read_only": True,
            },
        )
