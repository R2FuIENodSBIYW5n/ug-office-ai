"""Per-user OfficeClient management."""

from __future__ import annotations

import asyncio

from returns.maybe import Some
from returns.result import Failure, Result, Success

from .client import OfficeClient
from .models import APIError
from .user_registry import UserRegistry


class SessionStore:
    """Lazily creates and caches an OfficeClient per MCP user."""

    def __init__(self, registry: UserRegistry) -> None:
        self._registry = registry
        self._clients: dict[str, OfficeClient] = {}
        self._lock = asyncio.Lock()

    async def get_client(self, user_id: str) -> Result[OfficeClient, APIError]:
        """Get or create an OfficeClient for *user_id* (MCP username)."""
        if user_id in self._clients:
            return Success(self._clients[user_id])

        async with self._lock:
            # Double-check after acquiring lock
            if user_id in self._clients:
                return Success(self._clients[user_id])

            match self._registry.get_user(user_id):
                case Some(entry):
                    client = OfficeClient(
                        base_url=entry.ug_office_url,
                        username=entry.ug_username,
                        password=entry.ug_password,
                    )
                    self._clients[user_id] = client
                    return Success(client)
                case _:
                    return Failure(
                        APIError(error="unknown_user", detail=f"Unknown user: {user_id}")
                    )

    async def close_all(self) -> None:
        for client in self._clients.values():
            await client.close()
        self._clients.clear()
