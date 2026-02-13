"""Per-user Playwright browser context management."""

from __future__ import annotations

import asyncio
import logging

from playwright.async_api import Browser, BrowserContext, async_playwright
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success

from .models import APIError
from .user_registry import UserRegistry

logger = logging.getLogger(__name__)


class BrowserStore:
    """Lazily launches Chromium and manages per-user BrowserContexts.

    One shared Chromium process, multiple isolated BrowserContexts (each ~10-20 MB).
    Each context has its own cookies/storage — like an incognito window per user.
    """

    def __init__(self, registry: UserRegistry | None = None) -> None:
        self._registry = registry
        self._playwright = None
        self._browser: Maybe[Browser] = Nothing
        self._contexts: dict[str, BrowserContext] = {}
        self._lock = asyncio.Lock()

    async def _ensure_browser(self) -> Result[Browser, APIError]:
        """Lazily launch Chromium on first use.

        Must be called either under ``self._lock`` or before concurrent access.
        """
        match self._browser:
            case Some(browser):
                return Success(browser)
            case _:
                pass

        self._playwright = await async_playwright().start()
        try:
            browser = await self._playwright.chromium.launch(headless=True)
        except Exception as exc:
            await self._playwright.stop()
            self._playwright = None
            return Failure(
                APIError(
                    error="browser_launch_failed",
                    detail=(
                        f"Failed to launch Chromium: {exc}. "
                        "Run: uv run playwright install chromium"
                    ),
                )
            )
        self._browser = Some(browser)
        logger.info("Playwright Chromium launched")
        return Success(browser)

    async def get_context(self, user_id: str) -> Result[BrowserContext, APIError]:
        """Get or create an authenticated BrowserContext for *user_id*."""
        if user_id in self._contexts:
            return Success(self._contexts[user_id])

        async with self._lock:
            # Double-check after acquiring lock
            if user_id in self._contexts:
                return Success(self._contexts[user_id])

            if self._registry is None:
                return Failure(
                    APIError(error="no_registry", detail="No user registry configured")
                )

            match self._registry.get_user(user_id):
                case Some(entry):
                    pass
                case _:
                    return Failure(
                        APIError(error="unknown_user", detail=f"Unknown user: {user_id}")
                    )

            browser_result = await self._ensure_browser()
            match browser_result:
                case Failure(err):
                    return Failure(err)
                case Success(browser):
                    pass

            context = await browser.new_context()
            await self._login(context, entry.ug_web_url, entry.ug_username, entry.ug_password)
            self._contexts[user_id] = context
            logger.info("Browser context created for user %s", user_id)
            return Success(context)

    async def get_stdio_context(
        self, web_url: str, username: str, password: str
    ) -> Result[BrowserContext, APIError]:
        """Create a pre-authenticated context for stdio mode (no registry)."""
        async with self._lock:
            # Double-check after acquiring lock
            if "__stdio__" in self._contexts:
                return Success(self._contexts["__stdio__"])

            browser_result = await self._ensure_browser()
            match browser_result:
                case Failure(err):
                    return Failure(err)
                case Success(browser):
                    pass

            context = await browser.new_context()
            await self._login(context, web_url, username, password)
            self._contexts["__stdio__"] = context
            logger.info("Stdio browser context created")
            return Success(context)

    @staticmethod
    async def _login(
        context: BrowserContext, web_url: str, username: str, password: str
    ) -> None:
        """Auto-login to UG Office SPA via the login form."""
        # Store base URL on context for reliable URL resolution in tools
        context._ug_base_url = web_url  # type: ignore[attr-defined]

        page = await context.new_page()
        try:
            await page.goto(web_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            await page.fill('input[name="username"], input[type="text"]', username)
            await page.fill('input[name="password"], input[type="password"]', password)
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            logger.info("Browser login completed for %s", username)
        except Exception as exc:
            logger.warning("Browser login failed for %s: %s", username, exc)
            # Context still usable — some pages may not need auth
        finally:
            await page.close()

    async def close_all(self) -> None:
        """Close all contexts and the browser."""
        for key, ctx in list(self._contexts.items()):
            try:
                await ctx.close()
            except Exception:
                logger.warning("Failed to close browser context %s", key)
        self._contexts.clear()

        match self._browser:
            case Some(browser):
                try:
                    await browser.close()
                except Exception:
                    logger.warning("Failed to close browser")
                self._browser = Nothing
            case _:
                pass

        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                logger.warning("Failed to stop Playwright")
            self._playwright = None
        logger.info("All browser resources closed")
