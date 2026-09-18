"""Read-only endpoint discovery for an authenticated crawler API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .pagination import extract_items


@dataclass(frozen=True)
class ObservedEndpoint:
    path: str
    method: str
    status_code: int | None
    json_keys: list[str]
    pagination: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "method": self.method,
            "status_code": self.status_code,
            "json_keys": self.json_keys,
            "pagination": self.pagination,
            "error": self.error,
        }


class CrawlerDiscovery:
    DEFAULT_CANDIDATES = [
        "/api-non/v1.0/users/setup-status",
        "/api/v1.0/status",
        "/api/v1.0/user/get",
        "/api/v1.0/crawl/sources",
        "/api/v1.0/crawl/jobs",
        "/api/v1.0/crawl/pages",
        "/api/v1.0/crawl/exports",
        "/openapi.json",
    ]

    def __init__(self, client: httpx.Client, candidates: list[str] | None = None):
        self.client = client
        self.candidates = candidates or self.DEFAULT_CANDIDATES

    def probe(self) -> list[ObservedEndpoint]:
        observed: list[ObservedEndpoint] = []
        for path in self.candidates:
            try:
                response = self.client.get(path)
                keys: list[str] = []
                pagination = None
                try:
                    payload = response.json()
                    if isinstance(payload, dict):
                        data = payload.get("data", payload)
                        if isinstance(data, dict):
                            keys = sorted(str(key) for key in data.keys())
                            if {"items", "page", "page_size", "total"}.issubset(data):
                                pagination = "items/page/page_size/total"
                        elif isinstance(data, list):
                            keys = ["<array>"]
                except ValueError:
                    pass
                observed.append(ObservedEndpoint(path, "GET", response.status_code, keys, pagination))
            except httpx.HTTPError as exc:
                observed.append(ObservedEndpoint(path, "GET", None, [], error=exc.__class__.__name__))
        return observed
