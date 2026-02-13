"""JWT authentication manager for UG Office API."""

from __future__ import annotations

import time

import httpx
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success

from .models import APIError


class AuthManager:
    """Handles login and JWT token lifecycle for the UG Office API."""

    TOKEN_MAX_AGE = 30 * 60  # 30 minutes

    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._token: Maybe[str] = Nothing
        self._token_time: float = 0.0

    @property
    def token(self) -> Maybe[str]:
        return self._token

    @property
    def is_expired(self) -> bool:
        match self._token:
            case Some(_):
                return (time.time() - self._token_time) > self.TOKEN_MAX_AGE
            case _:
                return True

    async def login(self, client: httpx.AsyncClient) -> Result[str, APIError]:
        """Authenticate and return a fresh JWT token."""
        try:
            resp = await client.post(
                f"{self.base_url}/1.0/auth/login",
                json={"username": self.username, "password": self.password},
            )
            resp.raise_for_status()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            return Failure(APIError(error="login_failed", detail=str(exc)))

        auth_header = resp.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return Failure(
                APIError(
                    error="login_failed",
                    detail="Login succeeded but no Bearer token in response headers",
                )
            )

        token = auth_header.removeprefix("Bearer ")
        self._token = Some(token)
        self._token_time = time.time()
        return Success(token)

    async def get_token(self, client: httpx.AsyncClient) -> Result[str, APIError]:
        """Return a valid token, refreshing if expired."""
        if self.is_expired:
            return await self.login(client)
        match self._token:
            case Some(t):
                return Success(t)
            case _:
                return await self.login(client)

    def invalidate(self) -> None:
        """Force token refresh on next request."""
        self._token = Nothing
        self._token_time = 0.0
