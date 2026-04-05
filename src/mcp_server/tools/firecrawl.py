"""Firecrawl MCP - Web scraping with intelligent content extraction."""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False


FIRECRAWL_API = os.environ.get("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v0")
FIRECRAWL_TOKEN = os.environ.get("FIRECRAWL_API_TOKEN", "")


def _get_headers() -> dict:
    """Get headers for Firecrawl API."""
    headers = {
        "Content-Type": "application/json",
    }
    if FIRECRAWL_TOKEN:
        headers["Authorization"] = f"Bearer {FIRECRAWL_TOKEN}"
    return headers


def scrape_url(
    url: str,
    page_limit: int = 1,
    only_main_content: bool = True,
    include_html: bool = False,
) -> dict:
    """
    Scrape a URL with Firecrawl.

    Args:
        url: URL to scrape
        page_limit: Number of pages to crawl (default: 1)
        only_main_content: Only return main content (no nav/footers)
        include_html: Include raw HTML

    Returns:
        dict with keys: content, markdown, links, error
    """
    if not FIRECRAWL_TOKEN:
        return {
            "content": "",
            "markdown": "",
            "links": [],
            "error": "FIRECRAWL_API_TOKEN not set. Get one at https://firecrawl.dev",
        }

    if not HTTpx_AVAILABLE:
        return {"content": "", "markdown": "", "links": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{FIRECRAWL_API}/scrape",
                headers=_get_headers(),
                json={
                    "url": url,
                    "pageLimit": page_limit,
                    "onlyMainContent": only_main_content,
                    "includeHtml": include_html,
                },
            )
            response.raise_for_status()

        data = response.json()

        return {
            "content": data.get("content", ""),
            "markdown": data.get("markdown", ""),
            "links": data.get("links", []),
            "metadata": data.get("metadata", {}),
            "error": None,
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"content": "", "markdown": "", "links": [], "error": "Invalid Firecrawl API token"}
        return {"content": "", "markdown": "", "links": [], "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"content": "", "markdown": "", "links": [], "error": str(e)}


def crawl_url(
    url: str,
    limit: int = 10,
    allow_external: bool = False,
    include_html: bool = False,
) -> dict:
    """
    Crawl a URL with multiple pages.

    Args:
        url: Starting URL
        limit: Max pages to crawl
        allow_external: Allow crawling external domains
        include_html: Include raw HTML

    Returns:
        dict with keys: pages (list), error
    """
    if not FIRECRAWL_TOKEN:
        return {"pages": [], "error": "FIRECRAWL_API_TOKEN not set"}

    if not HTTpx_AVAILABLE:
        return {"pages": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{FIRECRAWL_API}/crawl",
                headers=_get_headers(),
                json={
                    "url": url,
                    "limit": limit,
                    "allowExternal": allow_external,
                    "includeHtml": include_html,
                },
            )
            response.raise_for_status()

        data = response.json()
        pages = []

        for item in data.get("data", []):
            pages.append({
                "url": item.get("url"),
                "content": item.get("content"),
                "markdown": item.get("markdown"),
                "metadata": item.get("metadata", {}),
            })

        return {"pages": pages, "total": len(pages), "error": None}
    except Exception as e:
        return {"pages": [], "error": str(e)}


def map_url(url: str) -> dict:
    """
    Get all URLs from a website.

    Args:
        url: Website to map

    Returns:
        dict with keys: urls (list), error
    """
    if not FIRECRAWL_TOKEN:
        return {"urls": [], "error": "FIRECRAWL_API_TOKEN not set"}

    if not HTTpx_AVAILABLE:
        return {"urls": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{FIRECRAWL_API}/map",
                headers=_get_headers(),
                json={"url": url},
            )
            response.raise_for_status()

        data = response.json()

        return {
            "urls": data.get("urls", []),
            "count": len(data.get("urls", [])),
            "error": None,
        }
    except Exception as e:
        return {"urls": [], "error": str(e)}


def batch_scrape(urls: List[str], only_main_content: bool = True) -> dict:
    """
    Scrape multiple URLs in batch.

    Args:
        urls: List of URLs to scrape
        only_main_content: Only return main content

    Returns:
        dict with keys: results (list), error
    """
    if not FIRECRAWL_TOKEN:
        return {"results": [], "error": "FIRECRAWL_API_TOKEN not set"}

    if not HTTpx_AVAILABLE:
        return {"results": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{FIRECRAWL_API}/batch/scrape",
                headers=_get_headers(),
                json={
                    "urls": urls,
                    "onlyMainContent": only_main_content,
                },
            )
            response.raise_for_status()

        data = response.json()
        results = []

        for item in data.get("data", []):
            results.append({
                "url": item.get("url"),
                "markdown": item.get("markdown", ""),
                "success": item.get("success", False),
            })

        return {"results": results, "total": len(results), "error": None}
    except Exception as e:
        return {"results": [], "error": str(e)}


# Fallback to local scraping if no API token
def scrape_local(url: str, max_length: int = 20000) -> dict:
    """
    Fallback local scraping when Firecrawl API is not available.

    Uses Playwright or basic HTTP fetch.
    """
    if HTTpx_AVAILABLE:
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/1.0)",
                })
                response.raise_for_status()

            from ..utils.html_processor import fetch_and_extract
            result = fetch_and_extract(url, max_length)

            return {
                "content": result.get("text", "")[:max_length],
                "markdown": result.get("text", "")[:max_length],
                "links": [l.get("href", "") for l in result.get("links", [])[:20]],
                "metadata": {"title": result.get("title", "")},
                "source": "local",
                "error": None,
            }
        except Exception as e:
            return {
                "content": "",
                "markdown": "",
                "links": [],
                "error": str(e),
                "source": "local",
            }

    return {
        "content": "",
        "markdown": "",
        "links": [],
        "error": "No scraping capability available",
    }