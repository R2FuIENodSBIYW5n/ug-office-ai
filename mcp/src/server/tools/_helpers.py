"""Shared helpers for tool modules."""

from __future__ import annotations

import os

from fastmcp import Context
from playwright.async_api import BrowserContext
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success

from ..client import OfficeClient
from ..models import APIError
from ..socketio_client import SocketIOManager

MAX_ERROR_DETAIL_LEN = 500


def sanitize_error(tool_name: str, exc: Exception) -> dict[str, str]:
    """Build an error dict from an exception, truncating long details."""
    detail = str(exc)[:MAX_ERROR_DETAIL_LEN]
    return APIError(
        error=f"{tool_name} failed: {type(exc).__name__}",
        detail=detail,
    ).model_dump()


def _get_access_token() -> Maybe:
    """Try to retrieve the OAuth access token, or Nothing."""
    try:
        from mcp.server.auth.middleware.auth_context import get_access_token

        token = get_access_token()
        return Some(token) if token is not None else Nothing
    except Exception:
        return Nothing


async def get_client(ctx: Context) -> Result[OfficeClient, APIError]:
    """Resolve the OfficeClient for the current request.

    In OAuth mode, looks up the per-user session via the bearer token.
    In stdio mode, falls back to the shared client from lifespan context.
    """
    match _get_access_token():
        case Some(token) if hasattr(token, "user_id"):
            session_store = ctx.lifespan_context["session_store"]
            return await session_store.get_client(token.user_id)
        case _:
            client = ctx.lifespan_context.get("client")
            if client is None:
                return Failure(
                    APIError(error="no_client", detail="No client configured")
                )
            return Success(client)


async def get_browser_context(ctx: Context) -> Result[BrowserContext, APIError]:
    """Resolve the per-user Playwright BrowserContext.

    In OAuth mode, looks up the per-user browser context via the bearer token.
    In stdio mode, falls back to the shared browser context from lifespan context.
    """
    match _get_access_token():
        case Some(token) if hasattr(token, "user_id"):
            browser_store = ctx.lifespan_context.get("browser_store")
            if browser_store is None:
                return Failure(
                    APIError(
                        error="no_browser_store",
                        detail="browser_store not found in lifespan context.",
                    )
                )
            return await browser_store.get_context(token.user_id)
        case _:
            pass

    # stdio fallback — lazily create on first use
    if "browser_context" in ctx.lifespan_context:
        return Success(ctx.lifespan_context["browser_context"])

    browser_store = ctx.lifespan_context.get("browser_store")
    if browser_store is None:
        return Failure(
            APIError(
                error="no_browser_store",
                detail="browser_store not found in lifespan context.",
            )
        )
    result = await browser_store.get_stdio_context(
        web_url=os.getenv("UG_WEB_URL", "https://www.ugoffice.com"),
        username=os.getenv("UG_USERNAME", ""),
        password=os.getenv("UG_PASSWORD", ""),
    )
    match result:
        case Success(stdio_ctx):
            ctx.lifespan_context["browser_context"] = stdio_ctx
            return Success(stdio_ctx)
        case Failure(err):
            return Failure(err)


async def get_socketio(ctx: Context) -> Result[SocketIOManager, APIError]:
    """Get the Socket.IO manager from lifespan context."""
    mgr = ctx.lifespan_context.get("socketio_manager")
    if mgr is None:
        return Failure(APIError(error="no_socketio", detail="SocketIO not configured"))
    return Success(mgr)
