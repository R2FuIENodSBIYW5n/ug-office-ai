"""Browser automation tools — navigate, screenshot, extract data from UG Office pages."""

from __future__ import annotations

import base64
import json
import logging
import os
from urllib.parse import urljoin

from fastmcp import Context, FastMCP
from returns.result import Failure, Result, Success

from ..models import APIError
from ._helpers import get_browser_context, sanitize_error

logger = logging.getLogger(__name__)


async def _safe_goto(page, url: str, settle_ms: int = 3000) -> Result[None, APIError]:
    """Navigate and wait for SPA render. Returns Success or Failure."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(settle_ms)
        return Success(None)
    except Exception as exc:
        err = APIError(
            error="navigation_failed",
            detail=f"Navigation to {url} failed: {exc}",
        )
        return Failure(err)


async def _resolve_url(ctx: Context, url: str) -> str:
    """Resolve a relative URL against the user's UG Office web URL."""
    if url.startswith(("http://", "https://")):
        return url
    ctx_result = await get_browser_context(ctx)
    match ctx_result:
        case Success(browser_ctx):
            base = getattr(browser_ctx, "_ug_base_url", None)
        case _:
            base = None
    if not base:
        base = os.getenv("UG_WEB_URL", "https://www.ugoffice.com")
    return urljoin(base, url)


def register(mcp: FastMCP) -> None:

    @mcp.tool
    async def browse_page(url: str, ctx: Context = None) -> str | dict:
        """Navigate to a UG Office page and return its text content.

        Args:
            url: Page URL — relative (e.g. '/settlement') or absolute.

        Returns the visible text content of the page.
        """
        match await get_browser_context(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(browser_ctx):
                resolved = await _resolve_url(ctx, url)
                page = await browser_ctx.new_page()
                try:
                    match await _safe_goto(page, resolved):
                        case Failure(err):
                            return err.model_dump()
                        case Success(_):
                            return await page.inner_text("body")
                finally:
                    await page.close()

    @mcp.tool
    async def screenshot_page(url: str, full_page: bool = True, ctx: Context = None) -> str | dict:
        """Take a screenshot of a UG Office page. Returns base64 PNG.

        Args:
            url: Page URL — relative or absolute.
            full_page: Capture entire scrollable page (default True).

        The MCP client (Claude) can view this as an image.
        """
        match await get_browser_context(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(browser_ctx):
                resolved = await _resolve_url(ctx, url)
                page = await browser_ctx.new_page()
                try:
                    match await _safe_goto(page, resolved):
                        case Failure(err):
                            return err.model_dump()
                        case Success(_):
                            png_bytes = await page.screenshot(full_page=full_page)
                            return base64.b64encode(png_bytes).decode("ascii")
                finally:
                    await page.close()

    @mcp.tool
    async def extract_table(
        url: str, table_selector: str = "table", ctx: Context = None
    ) -> list[dict] | dict:
        """Navigate to a page and extract HTML table data as structured JSON.

        Args:
            url: Page URL — relative or absolute.
            table_selector: CSS selector for the table element (default 'table').

        Returns list of row dicts with column headers as keys.
        """
        match await get_browser_context(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(browser_ctx):
                resolved = await _resolve_url(ctx, url)
                page = await browser_ctx.new_page()
                try:
                    match await _safe_goto(page, resolved):
                        case Failure(err):
                            return err.model_dump()
                        case Success(_):
                            js_code = """(selector) => {
                                const table = document.querySelector(selector);
                                if (!table) return null;
                                const headers = [
                                    ...table.querySelectorAll('thead th, tr:first-child th')
                                ].map(th => th.innerText.trim());
                                const bodyRows = [...table.querySelectorAll('tbody tr')];
                                if (bodyRows.length === 0) {
                                    const allRows = [...table.querySelectorAll('tr')];
                                    return allRows.slice(1).map(tr => {
                                        const tds = tr.querySelectorAll('td');
                                        const cells = [...tds].map(
                                            td => td.innerText.trim()
                                        );
                                        const obj = {};
                                        cells.forEach((c, i) => {
                                            const key = headers[i] || 'col_' + i;
                                            obj[key] = c;
                                        });
                                        return obj;
                                    });
                                }
                                return bodyRows.map(tr => {
                                    const tds = tr.querySelectorAll('td');
                                    const cells = [...tds].map(
                                        td => td.innerText.trim()
                                    );
                                    const obj = {};
                                    cells.forEach((c, i) => {
                                        const key = headers[i] || 'col_' + i;
                                        obj[key] = c;
                                    });
                                    return obj;
                                });
                            }"""
                            rows = await page.evaluate(js_code, table_selector)
                            if rows is None:
                                return {
                                    "error": "extract_table: no table found",
                                    "detail": f"Selector '{table_selector}' matched no elements",
                                }
                            return rows
                finally:
                    await page.close()

    @mcp.tool
    async def page_interact(url: str, actions: list[dict], ctx: Context = None) -> str | dict:
        """Navigate to a page, perform a sequence of interactions, return final text content.

        Args:
            url: Page URL — relative or absolute.
            actions: List of action dicts. Supported actions:
                - {"click": "css-selector"} — click an element
                - {"fill": ["css-selector", "value"]} — fill an input
                - {"wait": 1000} — wait N milliseconds
                - {"select": ["css-selector", "value"]} — select dropdown option

        Returns the visible text content of the page after all actions.
        """
        match await get_browser_context(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(browser_ctx):
                resolved = await _resolve_url(ctx, url)
                page = await browser_ctx.new_page()
                try:
                    match await _safe_goto(page, resolved):
                        case Failure(err):
                            return err.model_dump()
                        case Success(_):
                            for i, action in enumerate(actions):
                                try:
                                    if "click" in action:
                                        await page.click(action["click"])
                                    elif "fill" in action:
                                        selector, value = action["fill"]
                                        await page.fill(selector, value)
                                    elif "wait" in action:
                                        await page.wait_for_timeout(action["wait"])
                                    elif "select" in action:
                                        selector, value = action["select"]
                                        await page.select_option(selector, value)
                                except Exception as exc:
                                    return sanitize_error(
                                        f"page_interact action #{i}", exc
                                    )

                            await page.wait_for_load_state("domcontentloaded", timeout=30000)
                            return await page.inner_text("body")
                finally:
                    await page.close()

    @mcp.tool
    async def screenshot_winloss_report(
        date_from: str = "",
        date_to: str = "",
        ctx: Context = None,
    ) -> str | dict:
        """Screenshot the Win/Loss report from UG Office.

        Args:
            date_from: Optional start date filter (YYYY-MM-DD). Leave empty for default.
            date_to: Optional end date filter (YYYY-MM-DD). Leave empty for default.

        Returns base64 PNG screenshot of the report.
        """
        match await get_browser_context(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(browser_ctx):
                base = getattr(browser_ctx, "_ug_base_url", None)
                if not base:
                    base = os.getenv("UG_WEB_URL", "https://www.ugoffice.com")
                report_url = urljoin(base, "/reports/winloss/all")

                page = await browser_ctx.new_page()
                try:
                    match await _safe_goto(page, report_url):
                        case Failure(err):
                            return err.model_dump()
                        case Success(_):
                            # Apply date filters if provided
                            if date_from:
                                date_from_input = page.locator('input[type="date"]').first
                                await date_from_input.fill(date_from)
                            if date_to:
                                date_to_input = page.locator('input[type="date"]').last
                                await date_to_input.fill(date_to)

                            if date_from or date_to:
                                # Look for a submit/search/filter button and click it
                                for selector in [
                                    'button:has-text("Search")',
                                    'button:has-text("Filter")',
                                    'button:has-text("Apply")',
                                    'button:has-text("Submit")',
                                    'button[type="submit"]',
                                ]:
                                    btn = page.locator(selector).first
                                    if await btn.count() > 0:
                                        await btn.click()
                                        break
                                await page.wait_for_load_state("domcontentloaded", timeout=30000)
                                await page.wait_for_timeout(3000)

                            png_bytes = await page.screenshot(full_page=True)
                            return base64.b64encode(png_bytes).decode("ascii")
                finally:
                    await page.close()

    # Allowed domains for page_evaluate — only UG Office origins.
    _ALLOWED_EVAL_DOMAINS = {
        "ugoffice.com",
        "www.ugoffice.com",
    }

    def _is_allowed_eval_url(url: str) -> bool:
        """Check if a URL is on an allowed domain for JS evaluation."""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        # Also allow env-configured UG_WEB_URL domain
        allowed = set(_ALLOWED_EVAL_DOMAINS)
        env_url = os.getenv("UG_WEB_URL", "")
        if env_url:
            from urllib.parse import urlparse as _parse

            env_host = _parse(env_url).hostname
            if env_host:
                allowed.add(env_host)
        return hostname in allowed

    @mcp.tool
    async def page_evaluate(url: str, javascript: str, ctx: Context = None) -> str | dict:
        """[DESTRUCTIVE] Navigate to a page and evaluate JavaScript in the browser context.

        Executes arbitrary JavaScript in an authenticated browser session.
        Restricted to UG Office domains only. Never pass untrusted user input
        as the ``javascript`` argument.

        Side effects: Can modify page state, trigger API calls, or alter
        displayed data within the authenticated session.

        Args:
            url: Page URL — must be on an allowed UG Office domain.
            javascript: JavaScript expression to evaluate. Must return a serializable value.

        Returns the stringified result. Useful for extracting complex DOM data.
        """
        resolved = await _resolve_url(ctx, url)
        if not _is_allowed_eval_url(resolved):
            return APIError(
                error="domain_not_allowed",
                detail=f"page_evaluate is restricted to UG Office domains. Got: {resolved}",
            ).model_dump()

        match await get_browser_context(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(browser_ctx):
                page = await browser_ctx.new_page()
                try:
                    match await _safe_goto(page, resolved):
                        case Failure(err):
                            return err.model_dump()
                        case Success(_):
                            result = await page.evaluate(javascript)
                            if isinstance(result, (dict, list)):
                                return json.dumps(result, ensure_ascii=False, default=str)
                            return str(result)
                finally:
                    await page.close()
