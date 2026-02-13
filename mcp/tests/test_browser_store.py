"""Tests for BrowserStore."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from returns.maybe import Nothing, Some
from returns.result import Failure, Success

from server.browser_store import BrowserStore


class TestEnsureBrowser:
    @pytest.mark.asyncio
    async def test_launch_failure_returns_failure(self):
        store = BrowserStore()
        with patch("server.browser_store.async_playwright") as mock_apw:
            pw = AsyncMock()
            pw.chromium.launch = AsyncMock(side_effect=Exception("No chromium"))
            pw.stop = AsyncMock()

            cm = AsyncMock()
            cm.start = AsyncMock(return_value=pw)
            mock_apw.return_value = cm

            result = await store._ensure_browser()
            match result:
                case Failure(err):
                    assert "Failed to launch Chromium" in err.detail
                case _:
                    pytest.fail("Expected Failure")

            pw.stop.assert_called_once()
            assert store._playwright is None

    @pytest.mark.asyncio
    async def test_returns_existing_browser(self):
        store = BrowserStore()
        mock_browser = AsyncMock()
        store._browser = Some(mock_browser)
        result = await store._ensure_browser()
        assert result == Success(mock_browser)


class TestGetStdioContext:
    @pytest.mark.asyncio
    async def test_double_check_locking(self):
        """Calling get_stdio_context twice returns the same context."""
        store = BrowserStore()
        with patch("server.browser_store.async_playwright") as mock_apw:
            pw = AsyncMock()
            browser = AsyncMock()
            context = AsyncMock()
            page = AsyncMock()
            page.goto = AsyncMock()
            page.wait_for_timeout = AsyncMock()
            page.fill = AsyncMock()
            page.click = AsyncMock()
            page.wait_for_load_state = AsyncMock()
            page.close = AsyncMock()
            context.new_page = AsyncMock(return_value=page)
            browser.new_context = AsyncMock(return_value=context)
            pw.chromium.launch = AsyncMock(return_value=browser)
            pw.stop = AsyncMock()
            mock_apw.return_value.start = AsyncMock(return_value=pw)

            result1 = await store.get_stdio_context("https://test.com", "u", "p")
            result2 = await store.get_stdio_context("https://test.com", "u", "p")
            match (result1, result2):
                case (Success(ctx1), Success(ctx2)):
                    assert ctx1 is ctx2
                case _:
                    pytest.fail("Expected two Success results")
            # new_context should only be called once
            browser.new_context.assert_called_once()


class TestCloseAll:
    @pytest.mark.asyncio
    async def test_best_effort_close(self):
        """One context throwing doesn't prevent others from closing."""
        store = BrowserStore()
        ctx1 = AsyncMock()
        ctx1.close = AsyncMock(side_effect=Exception("close failed"))
        ctx2 = AsyncMock()
        ctx2.close = AsyncMock()
        store._contexts = {"a": ctx1, "b": ctx2}
        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        store._browser = Some(mock_browser)
        mock_pw = AsyncMock()
        mock_pw.stop = AsyncMock()
        store._playwright = mock_pw

        await store.close_all()

        ctx2.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_pw.stop.assert_called_once()
        assert store._browser == Nothing
        assert store._playwright is None
