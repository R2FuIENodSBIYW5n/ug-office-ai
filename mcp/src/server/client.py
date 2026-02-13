"""Async HTTP client wrapper with automatic JWT auth for UG Office API."""

from __future__ import annotations

import json
from typing import Any

import httpx
from returns.result import Failure, Result, Success

from .auth import AuthManager
from .models import APIError


MAX_RESPONSE_BYTES = 900_000  # Stay under Claude Desktop's 1 MB tool result limit


class OfficeClient:
    """Thin httpx wrapper that injects JWT auth and retries on 401."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth = AuthManager(self.base_url, username, password)
        self._http = httpx.AsyncClient(timeout=60.0)

    async def request(
        self, method: str, path: str, **kwargs: Any
    ) -> Result[dict[str, Any] | list[Any], APIError]:
        url = f"{self.base_url}{path}"

        token_result = await self.auth.get_token(self._http)
        match token_result:
            case Failure(err):
                return Failure(err)
            case Success(token):
                headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = await self._http.request(method, url, headers=headers, **kwargs)

            # Auto-retry once on 401
            if resp.status_code == 401:
                self.auth.invalidate()
                retry_result = await self.auth.get_token(self._http)
                match retry_result:
                    case Failure(err):
                        return Failure(err)
                    case Success(new_token):
                        headers = {"Authorization": f"Bearer {new_token}"}
                resp = await self._http.request(method, url, headers=headers, **kwargs)

            resp.raise_for_status()
            data = resp.json()

            # Truncate lists that would exceed Claude Desktop's 1 MB limit
            if isinstance(data, list) and len(json.dumps(data)) > MAX_RESPONSE_BYTES:
                truncated = []
                size = 2  # for []
                for item in data:
                    item_size = len(json.dumps(item)) + 1  # +1 for comma
                    if size + item_size > MAX_RESPONSE_BYTES - 200:
                        truncated.append(
                            {"_truncated": True, "shown": len(truncated), "total": len(data)}
                        )
                        break
                    truncated.append(item)
                    size += item_size
                data = truncated

            return Success(data)
        except httpx.HTTPStatusError as e:
            return Failure(
                APIError(
                    error=f"API returned {e.response.status_code}",
                    detail=e.response.text[:500],
                )
            )
        except httpx.RequestError as e:
            return Failure(
                APIError(
                    error=f"Request failed: {type(e).__name__}",
                    detail=str(e),
                )
            )
        except Exception as e:
            return Failure(
                APIError(
                    error=f"Unexpected error: {type(e).__name__}",
                    detail=str(e),
                )
            )

    async def get(
        self, path: str, **kwargs: Any
    ) -> Result[dict[str, Any] | list[Any], APIError]:
        return await self.request("GET", path, **kwargs)

    async def post(
        self, path: str, **kwargs: Any
    ) -> Result[dict[str, Any] | list[Any], APIError]:
        return await self.request("POST", path, **kwargs)

    async def put(
        self, path: str, **kwargs: Any
    ) -> Result[dict[str, Any] | list[Any], APIError]:
        return await self.request("PUT", path, **kwargs)

    async def delete(
        self, path: str, **kwargs: Any
    ) -> Result[dict[str, Any] | list[Any], APIError]:
        return await self.request("DELETE", path, **kwargs)

    async def close(self) -> None:
        await self._http.aclose()
