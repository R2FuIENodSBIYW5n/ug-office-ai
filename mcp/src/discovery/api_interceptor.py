"""Intercept and deduplicate API calls captured by Playwright."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class CapturedEndpoint:
    method: str
    path: str
    status: int | None = None
    content_type: str | None = None

    @property
    def key(self) -> str:
        return f"{self.method} {self.path}"


# Patterns to normalise dynamic path segments into :id placeholders
_ID_PATTERNS = [
    (re.compile(r"/\d{4,}"), "/:id"),  # numeric IDs (4+ digits)
    (re.compile(r"/[0-9a-f-]{36}"), "/:id"),  # UUIDs
]


def normalize_path(path: str) -> str:
    """Replace numeric IDs and UUIDs with :id placeholders."""
    for pattern, replacement in _ID_PATTERNS:
        path = pattern.sub(replacement, path)
    return path


class APIInterceptor:
    """Collects and deduplicates API requests seen during a Playwright session."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._seen: dict[str, CapturedEndpoint] = {}
        self._jwt_token: str | None = None

    @property
    def endpoints(self) -> list[CapturedEndpoint]:
        return sorted(self._seen.values(), key=lambda e: (e.path, e.method))

    @property
    def jwt_token(self) -> str | None:
        return self._jwt_token

    def on_request(self, request) -> None:
        """Playwright request handler."""
        url = request.url
        if not url.startswith(self.base_url):
            return

        # Capture JWT from request headers
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            self._jwt_token = auth.removeprefix("Bearer ")

        parsed = urlparse(url)
        path = normalize_path(parsed.path)
        method = request.method.upper()
        ep = CapturedEndpoint(method=method, path=path)
        self._seen.setdefault(ep.key, ep)

    def on_response(self, response) -> None:
        """Playwright response handler — enrich with status/content-type."""
        url = response.url
        if not url.startswith(self.base_url):
            return

        parsed = urlparse(url)
        path = normalize_path(parsed.path)
        method = response.request.method.upper()
        key = f"{method} {path}"
        if key in self._seen:
            self._seen[key].status = response.status
            self._seen[key].content_type = response.headers.get("content-type")

        # Also capture JWT from response headers
        auth = response.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            self._jwt_token = auth.removeprefix("Bearer ")
