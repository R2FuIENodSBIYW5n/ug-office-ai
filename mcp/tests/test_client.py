"""Tests for OfficeClient and AuthManager."""

from __future__ import annotations

import httpx
import pytest
import respx
from returns.maybe import Nothing, Some
from returns.result import Failure, Success

from server.auth import AuthManager
from server.client import OfficeClient

BASE = "https://api.test.ugoffice.com"


class TestAuthManager:
    def test_initial_state_expired(self):
        auth = AuthManager(BASE, "user", "pass")
        assert auth.token == Nothing
        assert auth.is_expired is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_login_returns_token(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(
                200,
                json={"success": True},
                headers={"authorization": "Bearer test-jwt-token"},
            )
        )
        auth = AuthManager(BASE, "user", "pass")
        async with httpx.AsyncClient() as client:
            result = await auth.login(client)
        assert result == Success("test-jwt-token")
        assert auth.is_expired is False

    @respx.mock
    @pytest.mark.asyncio
    async def test_login_no_bearer_returns_failure(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(200, json={}, headers={})
        )
        auth = AuthManager(BASE, "user", "pass")
        async with httpx.AsyncClient() as client:
            result = await auth.login(client)
        match result:
            case Failure(err):
                assert "no Bearer token" in err.detail
            case _:
                pytest.fail("Expected Failure")

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_token_auto_login(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(
                200,
                json={},
                headers={"authorization": "Bearer auto-token"},
            )
        )
        auth = AuthManager(BASE, "user", "pass")
        async with httpx.AsyncClient() as client:
            result = await auth.get_token(client)
        assert result == Success("auto-token")

    def test_invalidate(self):
        auth = AuthManager(BASE, "user", "pass")
        auth._token = Some("something")
        auth._token_time = 999999999999.0
        auth.invalidate()
        assert auth.token == Nothing
        assert auth.is_expired is True


class TestOfficeClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_auto_auth_on_first_request(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(
                200,
                json={},
                headers={"authorization": "Bearer jwt-123"},
            )
        )
        respx.get(f"{BASE}/1.0/test").mock(return_value=httpx.Response(200, json={"ok": True}))
        client = OfficeClient(BASE, "user", "pass")
        try:
            result = await client.get("/1.0/test")
            assert result == Success({"ok": True})
        finally:
            await client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_retry_on_401(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(
                200,
                json={},
                headers={"authorization": "Bearer jwt-456"},
            )
        )
        # First call returns 401, second succeeds
        respx.get(f"{BASE}/1.0/data").mock(
            side_effect=[
                httpx.Response(401, json={"error": "unauthorized"}),
                httpx.Response(200, json={"data": "ok"}),
            ]
        )
        client = OfficeClient(BASE, "user", "pass")
        try:
            result = await client.get("/1.0/data")
            assert result == Success({"data": "ok"})
        finally:
            await client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_failure_on_api_error(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(
                200,
                json={},
                headers={"authorization": "Bearer jwt-789"},
            )
        )
        respx.get(f"{BASE}/1.0/fail").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        client = OfficeClient(BASE, "user", "pass")
        try:
            result = await client.get("/1.0/fail")
            match result:
                case Failure(err):
                    assert "500" in err.error
                case _:
                    pytest.fail("Expected Failure")
        finally:
            await client.close()

    @respx.mock
    @pytest.mark.asyncio
    async def test_failure_on_network_error(self):
        respx.post(f"{BASE}/1.0/auth/login").mock(
            return_value=httpx.Response(
                200,
                json={},
                headers={"authorization": "Bearer jwt-net"},
            )
        )
        respx.get(f"{BASE}/1.0/timeout").mock(side_effect=httpx.ConnectError("Connection refused"))
        client = OfficeClient(BASE, "user", "pass")
        try:
            result = await client.get("/1.0/timeout")
            match result:
                case Failure(err):
                    assert "Request failed" in err.error
                case _:
                    pytest.fail("Expected Failure")
        finally:
            await client.close()
