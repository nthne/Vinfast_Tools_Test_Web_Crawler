"""Read-only source configuration inspection tool."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import ToolResult


def inspect_source(client: Any, source_id: str) -> ToolResult:
    source = client.get_source(source_id)
    config = source.get("crawl_config") or {}
    return ToolResult(
        tool_name="inspect_source",
        answer=f"Source {source_id} was read without mutation.",
        evidence=[
            {"field": "enabled", "observed": source.get("enabled")},
            {"field": "domain", "observed": source.get("domain")},
            {"field": "crawl_config", "observed": dict(config)},
            {"field": "rules", "observed": source.get("rules") or {}},
        ],
        metrics={
            "source_id": source.get("id") or source_id,
            "display_name": source.get("display_name") or source.get("name"),
            "domain": source.get("domain"),
            "enabled": source.get("enabled"),
            "max_pages": config.get("max_pages") if isinstance(config, Mapping) else None,
            "max_resources": config.get("max_resources") if isinstance(config, Mapping) else None,
            "max_depth": config.get("max_depth") if isinstance(config, Mapping) else None,
            "degraded": source.get("degraded") or [],
        },
    )
