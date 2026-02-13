"""Socket.IO client manager for live odds from io.ugoffice.com."""

from __future__ import annotations

import asyncio
import logging
from uuid import uuid4

import socketio

logger = logging.getLogger(__name__)


class SocketIOManager:
    """Manages Socket.IO connections to io.ugoffice.com for live odds."""

    def __init__(self, io_url: str = "https://io.ugoffice.com:443"):
        self.io_url = io_url
        self._client: socketio.AsyncClient | None = None
        self._pending: dict[str, asyncio.Future] = {}
        self._connected = False

    async def connect(self, jwt_token: str) -> None:
        """Connect to Socket.IO server with JWT auth."""
        if self._client is not None:
            await self.disconnect()

        self._client = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=3,
            reconnection_delay=1,
        )

        @self._client.event
        async def connect():
            self._connected = True
            logger.info("Socket.IO connected to %s", self.io_url)

        @self._client.event
        async def disconnect():
            self._connected = False
            logger.info("Socket.IO disconnected")

        @self._client.on("*")
        async def catch_all(event, *args):
            # Responses come back as positional args; first arg is the path+id, rest is data
            # The server sends responses matching the request id embedded in the path
            # e.g. event="get" isn't used; responses arrive as message events
            logger.debug("Socket.IO event %s: %s", event, str(args)[:200])

        # The server returns responses via ack callbacks on the emit,
        # or via numbered message events. We use the callback approach.
        try:
            await self._client.connect(
                self.io_url,
                transports=["websocket"],
                headers={"Authorization": f"Bearer {jwt_token}"},
            )
        except Exception:
            logger.exception("Socket.IO connection failed")
            self._client = None
            raise

    async def _rpc(self, path: str, payload: list[dict]) -> list[dict] | dict:
        """Send an RPC request and wait for the ack response.

        The website sends: 42["get", "/odds?id=<uuid>", [{...}]]
        python-socketio handles the 42 framing; we emit event="get".
        """
        if self._client is None or not self._connected:
            raise RuntimeError("Socket.IO not connected")

        request_id = str(uuid4())
        qualified_path = f"{path}?id={request_id}"

        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[request_id] = future

        try:
            # Use callback-based approach: emit with a callback
            response = await self._client.call("get", qualified_path, payload, timeout=15)
            return response
        except socketio.exceptions.TimeoutError:
            logger.warning("Socket.IO RPC timeout for %s", qualified_path)
            raise TimeoutError(f"Socket.IO request timed out: {path}")
        finally:
            self._pending.pop(request_id, None)

    async def get_odds(self, match_id: int, market_ids: list[int]) -> list[dict] | dict:
        """Send get /odds request and wait for response.

        Args:
            match_id: Internal match identifier.
            market_ids: List of market IDs to query.

        Returns:
            Odds data from the server.
        """
        payload = [
            {"sport_id": 1, "match_id": match_id, "market_id": mid}
            for mid in market_ids
        ]
        return await self._rpc("/odds", payload)

    async def get_match(self, sport_id: int, date: str) -> list[dict] | dict:
        """Send get /match request and wait for response.

        Args:
            sport_id: Sport identifier (1 = soccer).
            date: Date string (YYYY-MM-DD).

        Returns:
            Match data from the server.
        """
        payload = [{"sport_id": sport_id, "date": date}]
        return await self._rpc("/match", payload)

    async def disconnect(self) -> None:
        """Clean up connection."""
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception:
                logger.debug("Socket.IO disconnect error (ignored)", exc_info=True)
            self._client = None
            self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected
