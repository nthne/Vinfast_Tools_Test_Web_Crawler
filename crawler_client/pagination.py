"""Pagination helpers for common JSON envelope shapes."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from typing import Any


def extract_items(payload: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)], {}
    if not isinstance(payload, Mapping):
        return [], {}
    data = payload.get("data", payload)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)], {"total": len(data)}
    if isinstance(data, Mapping):
        items = data.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)], dict(data)
        nested = data.get("data")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)], dict(data)
    items = payload.get("items")
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)], dict(payload)
    return [], dict(payload)


def iter_paginated(
    fetch: Callable[[dict[str, Any]], Any],
    base_params: dict[str, Any] | None = None,
    page_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """Iterate page/page_size envelopes without assuming an offset or cursor API."""

    params = dict(base_params or {})
    page = int(params.pop("page", 1))
    seen_tokens: set[str] = set()
    while True:
        current = {**params, "page": page, "page_size": page_size}
        payload = fetch(current)
        items, meta = extract_items(payload)
        yield from items
        if not items:
            return
        total = meta.get("total")
        if isinstance(total, int) and page * page_size >= total:
            return
        next_token = meta.get("next_token") or meta.get("next_page_token") or meta.get("next")
        if next_token is not None:
            token = str(next_token)
            if not token or token in seen_tokens:
                return
            seen_tokens.add(token)
            params["cursor"] = next_token
            page += 1
        else:
            page += 1
