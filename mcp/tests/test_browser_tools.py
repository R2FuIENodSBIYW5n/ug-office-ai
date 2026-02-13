"""Tests for browser tool functions."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from returns.result import Failure, Success

from server.tools.browser import _resolve_url, _safe_goto


class TestSafeGoto:
    @pytest.mark.asyncio
    async def test_success_returns_success(self):
        page = AsyncMock()
        page.goto = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        result = await _safe_goto(page, "https://example.com")
        assert result == Success(None)
        page.goto.assert_called_once()

    @pytest.mark.asyncio
    async def test_failure_returns_failure(self):
        page = AsyncMock()
        page.goto = AsyncMock(side_effect=Exception("Timeout"))
        result = await _safe_goto(page, "https://example.com")
        match result:
            case Failure(err):
                assert "Navigation" in err.detail
                assert "Timeout" in err.detail
            case _:
                pytest.fail("Expected Failure")


class TestResolveUrl:
    @pytest.mark.asyncio
    async def test_absolute_url_unchanged(self):
        ctx = MagicMock()
        result = await _resolve_url(ctx, "https://example.com/page")
        assert result == "https://example.com/page"

    @pytest.mark.asyncio
    async def test_relative_url_uses_base(self):
        mock_browser_ctx = AsyncMock()
        mock_browser_ctx._ug_base_url = "https://test.ugoffice.com"

        ctx = MagicMock()
        with patch(
            "server.tools.browser.get_browser_context",
            return_value=Success(mock_browser_ctx),
        ):
            result = await _resolve_url(ctx, "/settlement")
        assert result == "https://test.ugoffice.com/settlement"


class TestBrowsePageErrors:
    """Test that browser tools return error dicts on exceptions."""

    @pytest.mark.asyncio
    async def test_browse_page_returns_error_on_failure(self):
        """When get_browser_context returns Failure, browse_page returns error dict."""
        from server.models import APIError
        from server.tools.browser import register

        mcp = MagicMock()
        tools = {}

        def capture_tool(fn):
            tools[fn.__name__] = fn
            return fn

        mcp.tool = capture_tool
        register(mcp)

        ctx = MagicMock()
        with patch(
            "server.tools.browser.get_browser_context",
            return_value=Failure(APIError(error="no_browser", detail="No browser")),
        ):
            result = await tools["browse_page"](url="/test", ctx=ctx)

        assert isinstance(result, dict)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_extract_table_returns_error_when_no_table(self):
        """extract_table returns error dict when JS returns null."""
        from server.tools.browser import register

        mcp = MagicMock()
        tools = {}

        def capture_tool(fn):
            tools[fn.__name__] = fn
            return fn

        mcp.tool = capture_tool
        register(mcp)

        page = AsyncMock()
        page.goto = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        page.evaluate = AsyncMock(return_value=None)
        page.close = AsyncMock()

        browser_ctx = AsyncMock()
        browser_ctx.new_page = AsyncMock(return_value=page)
        browser_ctx._ug_base_url = "https://test.ugoffice.com"

        ctx = MagicMock()
        with patch(
            "server.tools.browser.get_browser_context",
            return_value=Success(browser_ctx),
        ):
            result = await tools["extract_table"](
                url="https://test.ugoffice.com/page",
                table_selector="table",
                ctx=ctx,
            )

        assert isinstance(result, dict)
        assert "error" in result
        assert "no table found" in result["error"]

    @pytest.mark.asyncio
    async def test_page_evaluate_returns_error_on_failure(self):
        """page_evaluate returns error dict when get_browser_context returns Failure."""
        from server.models import APIError
        from server.tools.browser import register

        mcp = MagicMock()
        tools = {}

        def capture_tool(fn):
            tools[fn.__name__] = fn
            return fn

        mcp.tool = capture_tool
        register(mcp)

        ctx = MagicMock()
        with patch(
            "server.tools.browser.get_browser_context",
            return_value=Failure(APIError(error="no_browser", detail="No browser")),
        ):
            result = await tools["page_evaluate"](url="/test", javascript="1+1", ctx=ctx)

        assert isinstance(result, dict)
        assert "error" in result
