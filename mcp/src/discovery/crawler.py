"""Playwright-based crawler that logs in to the UG Office SPA and walks all menus."""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from .api_interceptor import APIInterceptor
from .generate_api_map import render_api_map

load_dotenv()

BASE_URL = os.getenv("UG_OFFICE_URL", "https://www.ugoffice.com")
USERNAME = os.getenv("UG_USERNAME", "alpha")
PASSWORD = os.getenv("UG_PASSWORD", "")


async def run_crawler() -> str:
    """Launch headless browser, login, walk menus, return api_map markdown."""
    interceptor = APIInterceptor(BASE_URL)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.on("request", interceptor.on_request)
        page.on("response", interceptor.on_response)

        # --- Login ---
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.fill('input[type="text"], input[name="username"]', USERNAME)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)

        # --- Walk sidebar menu items ---
        menu_items = await page.query_selector_all(
            "nav a, .sidebar a, .menu a, .nav-item a, [class*='menu'] a"
        )
        for item in menu_items:
            try:
                href = await item.get_attribute("href")
                if href and not href.startswith(("http", "javascript:", "#")):
                    await item.click()
                    await page.wait_for_load_state("domcontentloaded")
                    await page.wait_for_timeout(2000)

                    # Try clicking search/filter buttons to trigger data loads
                    for selector in [
                        'button:has-text("Search")',
                        'button:has-text("Filter")',
                        'button:has-text("Query")',
                        'button[type="submit"]',
                    ]:
                        btn = await page.query_selector(selector)
                        if btn:
                            try:
                                await btn.click()
                                await page.wait_for_load_state("domcontentloaded")
                                await page.wait_for_timeout(1000)
                            except Exception:
                                pass
            except Exception:
                continue

        await browser.close()

    return render_api_map(interceptor.endpoints)


def main() -> None:
    md = asyncio.run(run_crawler())
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "api_map.md")
    out_path = os.path.normpath(out_path)
    with open(out_path, "w") as f:
        f.write(md)
    print(f"Wrote {len(md)} bytes to {out_path}")


if __name__ == "__main__":
    main()
