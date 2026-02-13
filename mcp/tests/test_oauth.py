"""Tests for UGOAuthProvider."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.auth.provider import AuthorizeError
from returns.maybe import Some

from server.oauth_models import UGAccessToken, UGAuthorizationCode, UGRefreshToken
from server.oauth_provider import UGOAuthProvider
from server.user_registry import UserEntry


def _make_registry():
    """Create a mock UserRegistry."""
    registry = MagicMock()
    registry.verify = MagicMock(return_value=True)
    registry.get_user = MagicMock(
        return_value=Some(
            UserEntry(
                mcp_password="pass",
                ug_username="ug_user",
                ug_password="ug_pass",
                ug_office_url="https://api.test.ugoffice.com",
                ug_web_url="https://test.ugoffice.com",
            )
        )
    )
    return registry


def _make_client_info():
    """Create a mock OAuthClientInformationFull."""
    from mcp.shared.auth import OAuthClientInformationFull

    return OAuthClientInformationFull(
        client_id="test-client-id",
        client_secret="test-secret",
        redirect_uris=["https://localhost/callback"],
    )


def _make_auth_params():
    """Create a mock AuthorizationParams."""
    from mcp.server.auth.provider import AuthorizationParams

    return AuthorizationParams(
        state="test-state",
        scopes=["ug:read", "ug:write"],
        code_challenge="test-challenge",
        redirect_uri="https://localhost/callback",
        redirect_uri_provided_explicitly=True,
    )


class TestClientRegistration:
    @pytest.mark.asyncio
    async def test_register_and_get_client(self):
        provider = UGOAuthProvider(_make_registry(), "http://localhost:8000")
        client_info = _make_client_info()

        await provider.register_client(client_info)
        retrieved = await provider.get_client(client_info.client_id)
        assert retrieved is not None
        assert retrieved.client_id == client_info.client_id

    @pytest.mark.asyncio
    async def test_get_unknown_client_returns_none(self):
        provider = UGOAuthProvider(_make_registry(), "http://localhost:8000")
        assert await provider.get_client("nonexistent") is None


class TestAuthorization:
    @pytest.mark.asyncio
    async def test_authorize_returns_login_url(self):
        provider = UGOAuthProvider(_make_registry(), "http://localhost:8000")
        client_info = _make_client_info()
        params = _make_auth_params()

        url = await provider.authorize(client_info, params)
        assert "oauth/login" in url
        assert "session_id=" in url


class TestCompleteAuthorization:
    @pytest.mark.asyncio
    async def test_invalid_session_raises(self):
        provider = UGOAuthProvider(_make_registry(), "http://localhost:8000")

        with pytest.raises(AuthorizeError) as exc_info:
            await provider.complete_authorization("bad-session", "user", "pass")
        assert exc_info.value.error == "invalid_request"

    @pytest.mark.asyncio
    async def test_invalid_credentials_raises(self):
        registry = _make_registry()
        registry.verify = MagicMock(return_value=False)
        provider = UGOAuthProvider(registry, "http://localhost:8000")
        client_info = _make_client_info()
        params = _make_auth_params()

        url = await provider.authorize(client_info, params)
        session_id = url.split("session_id=")[1]

        with pytest.raises(AuthorizeError) as exc_info:
            await provider.complete_authorization(session_id, "user", "wrong")
        assert exc_info.value.error == "access_denied"

    @pytest.mark.asyncio
    async def test_full_auth_code_flow(self):
        """Register client -> authorize -> complete_authorization -> exchange."""

        registry = _make_registry()
        provider = UGOAuthProvider(registry, "http://localhost:8000")
        client_info = _make_client_info()
        params = _make_auth_params()

        await provider.register_client(client_info)

        # Authorize -> get session URL
        login_url = await provider.authorize(client_info, params)
        session_id = login_url.split("session_id=")[1]

        # Mock UG Office login call
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=mock_response)
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_http

            redirect_uri = await provider.complete_authorization(session_id, "user", "pass")

        assert "code=" in redirect_uri

        # Extract the code
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(redirect_uri)
        code = parse_qs(parsed.query)["code"][0]

        # Load and exchange code
        code_obj = await provider.load_authorization_code(client_info, code)
        assert code_obj is not None

        token = await provider.exchange_authorization_code(client_info, code_obj)
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.token_type == "Bearer"

        # Verify access token is valid
        access = await provider.load_access_token(token.access_token)
        assert access is not None
        assert access.user_id == "user"


class TestTokenRefresh:
    @pytest.mark.asyncio
    async def test_refresh_rotates_tokens(self):
        """Refreshing produces new tokens and invalidates old refresh token."""
        registry = _make_registry()
        provider = UGOAuthProvider(registry, "http://localhost:8000")
        client_info = _make_client_info()

        # Manually insert tokens
        import secrets

        old_access = secrets.token_urlsafe(16)
        old_refresh = secrets.token_urlsafe(16)

        provider._access_tokens[old_access] = UGAccessToken(
            token=old_access,
            client_id=client_info.client_id,
            scopes=["ug:read"],
            expires_at=int(time.time() + 3600),
            user_id="testuser",
        )
        provider._refresh_tokens[old_refresh] = UGRefreshToken(
            token=old_refresh,
            client_id=client_info.client_id,
            scopes=["ug:read"],
            expires_at=int(time.time() + 86400),
            user_id="testuser",
        )

        refresh_obj = await provider.load_refresh_token(client_info, old_refresh)
        assert refresh_obj is not None

        new_token = await provider.exchange_refresh_token(client_info, refresh_obj, ["ug:read"])

        # Old refresh token is gone
        assert await provider.load_refresh_token(client_info, old_refresh) is None
        # New tokens work
        assert await provider.load_access_token(new_token.access_token) is not None
        assert await provider.load_refresh_token(client_info, new_token.refresh_token) is not None


class TestExpiredToken:
    @pytest.mark.asyncio
    async def test_expired_access_token_rejected(self):
        provider = UGOAuthProvider(_make_registry(), "http://localhost:8000")

        provider._access_tokens["expired"] = UGAccessToken(
            token="expired",
            client_id="c",
            scopes=[],
            expires_at=int(time.time() - 10),
            user_id="u",
        )

        result = await provider.load_access_token("expired")
        assert result is None

    @pytest.mark.asyncio
    async def test_expired_auth_code_rejected(self):
        provider = UGOAuthProvider(_make_registry(), "http://localhost:8000")
        client_info = _make_client_info()

        provider._codes["expired-code"] = UGAuthorizationCode(
            code="expired-code",
            scopes=[],
            expires_at=time.time() - 10,
            client_id=client_info.client_id,
            code_challenge="ch",
            redirect_uri="https://localhost/callback",
            redirect_uri_provided_explicitly=True,
            user_id="u",
        )

        result = await provider.load_authorization_code(client_info, "expired-code")
        assert result is None
