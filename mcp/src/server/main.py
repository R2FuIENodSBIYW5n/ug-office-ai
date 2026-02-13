"""FastMCP server entrypoint for UG Office bridge."""

from __future__ import annotations

import html as html_mod
import logging
import os
import secrets
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastmcp import FastMCP
from returns.result import Success
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from .browser_store import BrowserStore
from .client import OfficeClient
from .socketio_client import SocketIOManager
from .tools import browser, members, operators, reports, settlement, sports, system, tickets
from . import prompts, resources

load_dotenv()

_transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

# These are set to non-None when running with OAuth (non-stdio)
_provider = None
_session_store = None
_registry = None


async def _token_cleanup_loop(interval: int = 300) -> None:
    """Periodically purge expired OAuth tokens."""
    import asyncio

    logger = logging.getLogger(__name__)
    while True:
        await asyncio.sleep(interval)
        if _provider is not None:
            removed = _provider.cleanup_expired()
            if removed:
                logger.info("OAuth token cleanup: removed %d expired entries", removed)


@asynccontextmanager
async def app_lifespan(mcp_server):
    import asyncio

    fallback_client: OfficeClient | None = None
    browser_store = BrowserStore(_registry)

    if _transport == "stdio":
        fallback_client = OfficeClient(
            base_url=os.getenv("UG_OFFICE_URL", "https://www.ugoffice.com"),
            username=os.getenv("UG_USERNAME", ""),
            password=os.getenv("UG_PASSWORD", ""),
        )

    socketio_manager = SocketIOManager()

    # Connect Socket.IO using the fallback client's JWT token
    if fallback_client is not None:
        try:
            token_result = await fallback_client.auth.get_token(fallback_client._http)
            match token_result:
                case Success(token):
                    await socketio_manager.connect(token)
                case _:
                    logging.getLogger(__name__).warning(
                        "Could not get JWT for Socket.IO — live odds unavailable"
                    )
        except Exception:
            logging.getLogger(__name__).warning(
                "Socket.IO connection failed — live odds unavailable", exc_info=True
            )

    ctx: dict = {
        "client": fallback_client,
        "browser_store": browser_store,
        "socketio_manager": socketio_manager,
    }
    if _session_store is not None:
        ctx["session_store"] = _session_store

    cleanup_task: asyncio.Task | None = None
    if _provider is not None:
        cleanup_task = asyncio.create_task(_token_cleanup_loop())

    try:
        yield ctx
    finally:
        if cleanup_task is not None:
            cleanup_task.cancel()
        await socketio_manager.disconnect()
        if fallback_client is not None:
            await fallback_client.close()
        if _session_store is not None:
            await _session_store.close_all()
        await browser_store.close_all()


def _build_mcp() -> FastMCP:
    """Build the FastMCP instance, optionally with OAuth for non-stdio transports."""
    global _provider, _session_store, _registry

    match _transport:
        case "stdio":
            server = FastMCP("UG Office", lifespan=app_lifespan)
            _register_health_route(server)
            return server
        case _:
            from .oauth_provider import UGOAuthProvider
            from .session_store import SessionStore
            from .user_registry import UserRegistry

            registry = UserRegistry()
            _registry = registry
            _session_store = SessionStore(registry)
            base_url = os.getenv("OAUTH_ISSUER_URL", "http://localhost:8000")

            _provider = UGOAuthProvider(registry, base_url)

            server = FastMCP(
                "UG Office",
                auth=_provider,
                lifespan=app_lifespan,
            )

            _register_login_routes(server)
            _register_health_route(server)
            return server


def _register_health_route(server: FastMCP) -> None:
    @server.custom_route("/health", methods=["GET"])
    async def health(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})


class _RateLimiter:
    """Simple in-memory rate limiter: max N attempts per IP per window."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60) -> None:
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window
        # Clean old entries
        self._attempts[ip] = [t for t in self._attempts[ip] if t > cutoff]
        if len(self._attempts[ip]) >= self.max_attempts:
            return False
        self._attempts[ip].append(now)
        return True


# CSRF token store: session_id -> (csrf_token, timestamp)
_csrf_tokens: dict[str, tuple[str, float]] = {}
_CSRF_TTL = 300  # 5 minutes

_login_limiter = _RateLimiter(max_attempts=5, window_seconds=60)


def _register_login_routes(server: FastMCP) -> None:
    from mcp.server.auth.provider import AuthorizeError

    provider = _provider
    assert provider is not None

    @server.custom_route("/oauth/login", methods=["GET"])
    async def login_form(request: Request) -> HTMLResponse:
        global _csrf_tokens
        session_id = html_mod.escape(request.query_params.get("session_id", ""))
        csrf_token = secrets.token_urlsafe(32)
        # Purge expired CSRF tokens
        now = time.time()
        _csrf_tokens = {k: v for k, v in _csrf_tokens.items() if now - v[1] < _CSRF_TTL}
        _csrf_tokens[session_id] = (csrf_token, now)
        html = f"""\
<!DOCTYPE html>
<html>
<head><title>UG Office MCP — Sign In</title></head>
<body>
<h2>Sign in to UG Office MCP</h2>
<form method="post" action="/oauth/login">
  <input type="hidden" name="session_id" value="{session_id}">
  <input type="hidden" name="csrf_token" value="{csrf_token}">
  <label>Username<br><input name="username" required></label><br><br>
  <label>Password<br><input name="password" type="password" required></label><br><br>
  <button type="submit">Sign In</button>
</form>
</body>
</html>"""
        return HTMLResponse(html)

    @server.custom_route("/oauth/login", methods=["POST"])
    async def login_submit(
        request: Request,
    ) -> RedirectResponse | HTMLResponse | JSONResponse:
        client_ip = request.client.host if request.client else "unknown"
        if not _login_limiter.is_allowed(client_ip):
            return JSONResponse(
                {"error": "Too many login attempts. Try again later."},
                status_code=429,
            )

        form = await request.form()
        session_id = str(form.get("session_id", ""))
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))
        csrf_token = str(form.get("csrf_token", ""))

        # Validate CSRF token
        csrf_entry = _csrf_tokens.pop(session_id, None)
        expected_csrf = csrf_entry[0] if csrf_entry else None
        if not expected_csrf or not secrets.compare_digest(csrf_token, expected_csrf):
            return HTMLResponse(
                "<h2>Invalid request</h2><p>CSRF validation failed.</p>",
                status_code=403,
            )

        try:
            redirect_uri = await provider.complete_authorization(session_id, username, password)
        except AuthorizeError as exc:
            desc = html_mod.escape(exc.error_description or exc.error)
            safe_sid = html_mod.escape(session_id)
            error_page = f"""\
<!DOCTYPE html>
<html>
<head><title>Login Failed</title></head>
<body>
<h2>Login failed</h2>
<p>{desc}</p>
<a href="/oauth/login?session_id={safe_sid}">Try again</a>
</body>
</html>"""
            return HTMLResponse(error_page, status_code=403)

        return RedirectResponse(redirect_uri, status_code=302)


mcp = _build_mcp()

# Register all tool modules
settlement.register(mcp)
sports.register(mcp)
tickets.register(mcp)
reports.register(mcp)
operators.register(mcp)
members.register(mcp)
system.register(mcp)
browser.register(mcp)

# Register MCP resources (read-only reference data)
resources.register(mcp)

# Register MCP prompts (workflow templates)
prompts.register(mcp)


def main() -> None:
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    match _transport:
        case "sse":
            mcp.run(
                transport="sse",
                host=os.getenv("MCP_HOST", "0.0.0.0"),
                port=int(os.getenv("MCP_PORT", "8000")),
            )
        case _:
            mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
