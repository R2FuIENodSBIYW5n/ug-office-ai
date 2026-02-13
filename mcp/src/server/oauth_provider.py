"""OAuth 2.1 Authorization Server provider bridging MCP auth to UG Office."""

from __future__ import annotations

import os
import secrets
import time

import httpx
from fastmcp.server.auth import OAuthProvider
from mcp.server.auth.provider import (
    AuthorizationParams,
    AuthorizeError,
    construct_redirect_uri,
)
from mcp.server.auth.settings import ClientRegistrationOptions
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from returns.maybe import Some

from .oauth_models import UGAccessToken, UGAuthorizationCode, UGRefreshToken
from .user_registry import UserRegistry

# Token lifetimes (seconds) — configurable via env vars
ACCESS_TOKEN_TTL = int(os.getenv("OAUTH_ACCESS_TOKEN_TTL", "3600"))
REFRESH_TOKEN_TTL = int(os.getenv("OAUTH_REFRESH_TOKEN_TTL", "86400"))
AUTH_CODE_TTL = int(os.getenv("OAUTH_AUTH_CODE_TTL", "300"))


class UGOAuthProvider(OAuthProvider):
    """In-memory OAuth provider that bridges MCP clients to UG Office credentials."""

    def __init__(self, registry: UserRegistry, base_url: str) -> None:
        super().__init__(
            base_url=base_url,
            client_registration_options=ClientRegistrationOptions(
                enabled=True,
                valid_scopes=["ug:read", "ug:write"],
                default_scopes=["ug:read", "ug:write"],
            ),
        )
        self._registry = registry

        # In-memory stores
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._codes: dict[str, UGAuthorizationCode] = {}
        self._access_tokens: dict[str, UGAccessToken] = {}
        self._refresh_tokens: dict[str, UGRefreshToken] = {}

        # Pending authorization sessions (session_id -> AuthorizationParams + client)
        self._pending: dict[str, dict] = {}

    # --- Client registration ---

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        self._clients[client_info.client_id] = client_info

    # --- Authorization ---

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        session_id = secrets.token_urlsafe(32)
        self._pending[session_id] = {
            "client": client,
            "params": params,
        }
        base = str(self.base_url).rstrip("/")
        return f"{base}/oauth/login?session_id={session_id}"

    async def complete_authorization(
        self, session_id: str, username: str, password: str
    ) -> str:
        """Validate credentials and return the redirect URI with an auth code.

        Called from the login form POST handler.
        """
        pending = self._pending.pop(session_id, None)
        if pending is None:
            raise AuthorizeError(
                error="invalid_request",
                error_description="Invalid or expired session",
            )

        client: OAuthClientInformationFull = pending["client"]
        params: AuthorizationParams = pending["params"]

        # Verify against user registry
        if not self._registry.verify(username, password):
            raise AuthorizeError(
                error="access_denied",
                error_description="Invalid username or password",
            )

        # Test that the UG Office credentials actually work
        match self._registry.get_user(username):
            case Some(entry):
                pass
            case _:
                raise AuthorizeError(
                    error="server_error",
                    error_description="User entry not found after verification",
                )

        async with httpx.AsyncClient(timeout=15.0) as http:
            try:
                resp = await http.post(
                    f"{entry.ug_office_url.rstrip('/')}/1.0/auth/login",
                    json={"username": entry.ug_username, "password": entry.ug_password},
                )
                resp.raise_for_status()
            except (httpx.HTTPError, httpx.RequestError) as exc:
                raise AuthorizeError(
                    error="server_error",
                    error_description=f"UG Office login failed: {exc}",
                )

        # Generate authorization code
        code = secrets.token_urlsafe(32)
        self._codes[code] = UGAuthorizationCode(
            code=code,
            scopes=params.scopes or [],
            expires_at=time.time() + AUTH_CODE_TTL,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
            user_id=username,
        )

        return construct_redirect_uri(
            str(params.redirect_uri),
            code=code,
            state=params.state,
        )

    # --- Authorization code exchange ---

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> UGAuthorizationCode | None:
        code_obj = self._codes.get(authorization_code)
        if code_obj is None:
            return None
        if code_obj.client_id != client.client_id:
            return None
        if time.time() > code_obj.expires_at:
            self._codes.pop(authorization_code, None)
            return None
        return code_obj

    async def exchange_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: UGAuthorizationCode,
    ) -> OAuthToken:
        # Single-use: remove the code
        self._codes.pop(authorization_code.code, None)

        now = time.time()
        access_token_str = secrets.token_urlsafe(32)
        refresh_token_str = secrets.token_urlsafe(32)

        self._access_tokens[access_token_str] = UGAccessToken(
            token=access_token_str,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=int(now + ACCESS_TOKEN_TTL),
            resource=authorization_code.resource,
            user_id=authorization_code.user_id,
        )
        self._refresh_tokens[refresh_token_str] = UGRefreshToken(
            token=refresh_token_str,
            client_id=client.client_id,
            scopes=authorization_code.scopes,
            expires_at=int(now + REFRESH_TOKEN_TTL),
            user_id=authorization_code.user_id,
        )

        return OAuthToken(
            access_token=access_token_str,
            token_type="Bearer",
            expires_in=ACCESS_TOKEN_TTL,
            scope=" ".join(authorization_code.scopes) if authorization_code.scopes else None,
            refresh_token=refresh_token_str,
        )

    # --- Access token ---

    async def load_access_token(self, token: str) -> UGAccessToken | None:
        tok = self._access_tokens.get(token)
        if tok is None:
            return None
        if tok.expires_at is not None and time.time() > tok.expires_at:
            self._access_tokens.pop(token, None)
            return None
        return tok

    # --- Refresh token ---

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> UGRefreshToken | None:
        tok = self._refresh_tokens.get(refresh_token)
        if tok is None:
            return None
        if tok.client_id != client.client_id:
            return None
        if tok.expires_at is not None and time.time() > tok.expires_at:
            self._refresh_tokens.pop(refresh_token, None)
            return None
        return tok

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: UGRefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        # Rotate: remove old tokens
        self._refresh_tokens.pop(refresh_token.token, None)

        now = time.time()
        new_access = secrets.token_urlsafe(32)
        new_refresh = secrets.token_urlsafe(32)
        effective_scopes = scopes if scopes else refresh_token.scopes

        self._access_tokens[new_access] = UGAccessToken(
            token=new_access,
            client_id=client.client_id,
            scopes=effective_scopes,
            expires_at=int(now + ACCESS_TOKEN_TTL),
            user_id=refresh_token.user_id,
        )
        self._refresh_tokens[new_refresh] = UGRefreshToken(
            token=new_refresh,
            client_id=client.client_id,
            scopes=effective_scopes,
            expires_at=int(now + REFRESH_TOKEN_TTL),
            user_id=refresh_token.user_id,
        )

        return OAuthToken(
            access_token=new_access,
            token_type="Bearer",
            expires_in=ACCESS_TOKEN_TTL,
            scope=" ".join(effective_scopes) if effective_scopes else None,
            refresh_token=new_refresh,
        )

    # --- Revocation ---

    async def revoke_token(self, token: UGAccessToken | UGRefreshToken) -> None:
        match token:
            case UGAccessToken():
                self._access_tokens.pop(token.token, None)
            case UGRefreshToken():
                self._refresh_tokens.pop(token.token, None)

    def cleanup_expired(self) -> int:
        """Remove expired tokens from all stores. Returns count of removed entries."""
        now = time.time()
        count = 0
        for store in (self._codes, self._access_tokens, self._refresh_tokens):
            expired = [k for k, v in store.items() if v.expires_at and now > v.expires_at]
            for k in expired:
                del store[k]
                count += 1
        return count
