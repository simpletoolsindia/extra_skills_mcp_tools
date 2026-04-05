"""Browserbase MCP - Cloud browser automation with stealth browsing."""

from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False


BROWSERBASE_API = "https://browserbase.com/api/v1"
BROWSERBASE_TOKEN = os.environ.get("BROWSERBASE_API_KEY", "")
BROWSERBASE_PROJECT = os.environ.get("BROWSERBASE_PROJECT_ID", "")


def _get_headers() -> dict:
    """Get headers for Browserbase API."""
    headers = {"x-bb-key": BROWSERBASE_TOKEN} if BROWSERBASE_TOKEN else {}
    return headers


def create_session(
    project_id: Optional[str] = None,
    headless: bool = True,
    stealth: bool = True,
) -> dict:
    """
    Create a browser session.

    Args:
        project_id: Browserbase project ID
        headless: Run browser headless
        stealth: Enable stealth mode (block ads, fingerprints)

    Returns:
        dict with keys: session_id, preview_url, error
    """
    if not BROWSERBASE_TOKEN:
        return {"session_id": "", "preview_url": "", "error": "BROWSERBASE_API_KEY not set"}

    if not HTTpx_AVAILABLE:
        return {"session_id": "", "preview_url": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{BROWSERBASE_API}/sessions",
                headers=_get_headers(),
                json={
                    "projectId": project_id or BROWSERBASE_PROJECT,
                    "headless": headless,
                    "stealth": stealth,
                },
            )
            response.raise_for_status()

        data = response.json()

        return {
            "session_id": data.get("id"),
            "preview_url": data.get("previewUrl"),
            "status": data.get("status"),
            "error": None,
        }
    except Exception as e:
        return {"session_id": "", "preview_url": "", "error": str(e)}


def navigate(session_id: str, url: str) -> dict:
    """
    Navigate to URL in session.

    Args:
        session_id: Browser session ID
        url: URL to navigate to

    Returns:
        dict with keys: success, url, error
    """
    if not BROWSERBASE_TOKEN:
        return {"success": False, "url": "", "error": "BROWSERBASE_API_KEY not set"}

    if not HTTpx_AVAILABLE:
        return {"success": False, "url": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{BROWSERBASE_API}/sessions/{session_id}/navigate",
                headers=_get_headers(),
                json={"url": url},
            )
            response.raise_for_status()

        return {
            "success": True,
            "url": url,
            "error": None,
        }
    except Exception as e:
        return {"success": False, "url": "", "error": str(e)}


def get_dom(session_id: str) -> dict:
    """Get DOM content of current page."""
    if not BROWSERBASE_TOKEN:
        return {"dom": "", "error": "BROWSERBASE_API_KEY not set"}

    if not HTTpx_AVAILABLE:
        return {"dom": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{BROWSERBASE_API}/sessions/{session_id}/dom",
                headers=_get_headers(),
            )
            response.raise_for_status()

        return {
            "dom": response.json().get("dom", ""),
            "error": None,
        }
    except Exception as e:
        return {"dom": "", "error": str(e)}


def execute_script(session_id: str, script: str) -> dict:
    """Execute JavaScript in browser."""
    if not BROWSERBASE_TOKEN:
        return {"result": None, "error": "BROWSERBASE_API_KEY not set"}

    if not HTTpx_AVAILABLE:
        return {"result": None, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{BROWSERBASE_API}/sessions/{session_id}/execute",
                headers=_get_headers(),
                json={"script": script},
            )
            response.raise_for_status()

        return {
            "result": response.json().get("result"),
            "error": None,
        }
    except Exception as e:
        return {"result": None, "error": str(e)}


def click_element(session_id: str, selector: str) -> dict:
    """Click an element by CSS selector."""
    return execute_script(
        session_id,
        f"document.querySelector('{selector}').click()"
    )


def fill_input(session_id: str, selector: str, value: str) -> dict:
    """Fill an input field."""
    return execute_script(
        session_id,
        f"document.querySelector('{selector}').value = '{value}'"
    )


def take_screenshot(session_id: str) -> dict:
    """Take screenshot of current page."""
    if not BROWSERBASE_TOKEN:
        return {"screenshot": "", "error": "BROWSERBASE_API_KEY not set"}

    if not HTTpx_AVAILABLE:
        return {"screenshot": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{BROWSERBASE_API}/sessions/{session_id}/screenshot",
                headers=_get_headers(),
            )
            response.raise_for_status()

        import base64
        img_data = response.json().get("screenshot", "")
        if not img_data.startswith("data:"):
            img_data = f"data:image/png;base64,{img_data}"

        return {"screenshot": img_data, "error": None}
    except Exception as e:
        return {"screenshot": "", "error": str(e)}


def close_session(session_id: str) -> dict:
    """Close a browser session."""
    if not BROWSERBASE_TOKEN:
        return {"success": False, "error": "BROWSERBASE_API_KEY not set"}

    if not HTTpx_AVAILABLE:
        return {"success": False, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.delete(
                f"{BROWSERBASE_API}/sessions/{session_id}",
                headers=_get_headers(),
            )
            response.raise_for_status()

        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Fallback to Playwright if no Browserbase credentials
def fallback_browse(
    url: str,
    action: str = "get_content",
    selector: Optional[str] = None,
    wait_for: Optional[str] = None,
) -> dict:
    """
    Fallback to Playwright when Browserbase is not available.

    Args:
        url: URL to browse
        action: 'get_content', 'screenshot', 'click', 'fill'
        selector: CSS selector for actions
        wait_for: Element to wait for

    Returns:
        dict with keys: content, screenshot, error
    """
    if HTTpx_AVAILABLE:
        try:
            from .playwright_scrape import scrape_dynamic_page

            # Check if it's async
            import asyncio
            result = asyncio.run(scrape_dynamic_page(
                url=url,
                selector=selector,
                wait_for=wait_for,
            ))

            if action == "screenshot":
                # Use playwright screenshot
                return {
                    "content": result.get("text", ""),
                    "screenshot": result.get("screenshot", ""),
                    "error": result.get("error"),
                }

            return result

        except Exception as e:
            return {"content": "", "screenshot": "", "error": str(e)}

    return {"content": "", "screenshot": "", "error": "No browser automation available"}