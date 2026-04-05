"""Playwright-based web scraping for dynamic JavaScript-heavy pages."""

from __future__ import annotations

import os
import json
from typing import Optional

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


PLAYWRIGHT_HEADLESS = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
BROWSER_TIMEOUT = float(os.environ.get("BROWSER_TIMEOUT", "15"))


async def _get_browser() -> Optional[Browser]:
    """Get or create a shared browser instance."""
    if not PLAYWRIGHT_AVAILABLE:
        return None
    playwright = await async_playwright().start()
    return await playwright.chromium.launch(headless=PLAYWRIGHT_HEADLESS)


async def scrape_dynamic_page(
    url: str,
    selector: Optional[str] = None,
    wait_for: Optional[str] = None,
    max_length: int = 15000,
) -> dict:
    """
    Scrape a dynamic JavaScript-heavy page using Playwright.

    Args:
        url: The URL to scrape
        selector: Optional CSS selector to extract specific content
        wait_for: Optional CSS selector to wait for before extracting
        max_length: Maximum characters of text to return

    Returns:
        dict with keys: title, text, url, links, error
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "title": "",
            "text": "",
            "url": url,
            "links": [],
            "error": "Playwright not installed. Run: pip install playwright && playwright install chromium",
        }

    browser = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=PLAYWRIGHT_HEADLESS,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Set timeout
        page.set_default_timeout(BROWSER_TIMEOUT * 1000)

        # Navigate to page
        await page.goto(url, wait_until="domcontentloaded")

        # Wait for specific selector if provided
        if wait_for:
            try:
                await page.wait_for_selector(wait_for, timeout=5000)
            except Exception:
                pass  # Continue even if selector not found

        # Get title
        title = await page.title()

        # Extract content
        if selector:
            content_element = await page.query_selector(selector)
            if content_element:
                text = await content_element.inner_text()
            else:
                text = await page.content()
        else:
            # Get main content
            text = await page.inner_text("body")

        # Get links
        links = []
        a_elements = await page.query_selector_all("a[href]")
        for a in a_elements[:20]:
            href = await a.get_attribute("href")
            text_content = await a.inner_text()
            if href and text_content.strip():
                links.append({
                    "text": text_content.strip()[:100],
                    "href": href,
                })

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated]"

        final_url = page.url

        await context.close()
        await playwright.stop()

        return {
            "title": title,
            "text": text,
            "url": final_url,
            "links": links,
            "error": None,
        }

    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            error_msg = "Page load timed out"
        return {
            "title": "",
            "text": "",
            "url": url,
            "links": [],
            "error": error_msg,
        }
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass


async def screenshot_page(url: str, full_page: bool = False) -> dict:
    """
    Take a screenshot of a page.

    Args:
        url: The URL to screenshot
        full_page: Whether to capture the full scrollable page

    Returns:
        dict with keys: screenshot (base64), url, error
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "screenshot": None,
            "url": url,
            "error": "Playwright not installed",
        }

    browser = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=PLAYWRIGHT_HEADLESS,
            args=["--no-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()
        page.set_default_timeout(BROWSER_TIMEOUT * 1000)

        await page.goto(url, wait_until="networkidle")
        screenshot_bytes = await page.screenshot(full_page=full_page)

        await context.close()
        await playwright.stop()

        return {
            "screenshot": screenshot_bytes.decode("base64") if screenshot_bytes else None,
            "url": page.url,
            "error": None,
        }
    except Exception as e:
        return {
            "screenshot": None,
            "url": url,
            "error": str(e),
        }
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass