"""Shared test fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_http():
    """Mock httpx.AsyncClient."""
    client = AsyncMock()
    return client


@pytest.fixture
def mock_browser_context():
    """Mock Playwright BrowserContext."""
    ctx = AsyncMock()
    ctx._ug_base_url = "https://test.ugoffice.com"

    page = AsyncMock()
    page.inner_text = AsyncMock(return_value="page content")
    page.screenshot = AsyncMock(return_value=b"\x89PNG\r\n")
    page.evaluate = AsyncMock(return_value=[{"col": "val"}])
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.close = AsyncMock()
    page.fill = AsyncMock()
    page.click = AsyncMock()
    page.select_option = AsyncMock()
    page.locator = MagicMock()

    ctx.new_page = AsyncMock(return_value=page)
    return ctx


@pytest.fixture
def mock_mcp_context(mock_browser_context):
    """Mock FastMCP Context with lifespan_context."""
    ctx = MagicMock()
    ctx.lifespan_context = {
        "browser_store": MagicMock(),
        "browser_context": mock_browser_context,
    }
    return ctx
