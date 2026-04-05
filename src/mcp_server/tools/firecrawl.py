"""Firecrawl MCP - Self-hosted web scraping with intelligent content extraction."""

from __future__ import annotations

import os
import asyncio
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

# Self-hosted Firecrawl URL (set via environment or Docker service)
FIRECRAWL_HOST = os.environ.get("FIRECRAWL_HOST", "http://localhost:3002")
FIRECRAWL_TOKEN = os.environ.get("FIRECRAWL_API_TOKEN", "")  # Optional for self-hosted


def _get_headers() -> dict:
    """Get headers for Firecrawl API."""
    headers = {"Content-Type": "application/json"}
    if FIRECRAWL_TOKEN:
        headers["Authorization"] = f"Bearer {FIRECRAWL_TOKEN}"
    return headers


def _is_self_hosted_available() -> bool:
    """Check if self-hosted Firecrawl is running."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{FIRECRAWL_HOST}/health")
            return response.status_code == 200
    except Exception:
        return False


def _scrape_with_playwright(url: str, only_main_content: bool = True) -> dict:
    """
    Fallback scraping using Playwright (self-hosted).

    Args:
        url: URL to scrape
        only_main_content: Only return main content

    Returns:
        dict with keys: content, markdown, links, metadata, error
    """
    try:
        from .playwright_scrape import scrape_dynamic_page
        result = asyncio.run(scrape_dynamic_page(url=url))
        return {
            "content": result.get("text", ""),
            "markdown": result.get("text", ""),
            "links": result.get("links", []),
            "metadata": {"title": result.get("title", "")},
            "source": "playwright",
            "error": None,
        }
    except Exception as e:
        return {
            "content": "",
            "markdown": "",
            "links": [],
            "error": str(e),
            "source": "playwright",
        }


def _scrape_with_scrapling(url: str) -> dict:
    """
    Fallback scraping using Scrapling (self-hosted).

    Args:
        url: URL to scrape

    Returns:
        dict with keys: content, markdown, links, metadata, error
    """
    try:
        from .scrapling_extract import extract_structured
        result = extract_structured(
            url=url,
            query="Extract all text content from the main article body",
            output_format="markdown"
        )
        return {
            "content": result.get("content", ""),
            "markdown": result.get("markdown", result.get("content", "")),
            "links": result.get("links", []),
            "metadata": result.get("metadata", {}),
            "source": "scrapling",
            "error": None,
        }
    except Exception as e:
        return {
            "content": "",
            "markdown": "",
            "links": [],
            "error": str(e),
            "source": "scrapling",
        }


def _scrape_with_webclaw(url: str) -> dict:
    """
    Fallback scraping using Webclaw (self-hosted).

    Args:
        url: URL to scrape

    Returns:
        dict with keys: content, markdown, links, metadata, error
    """
    try:
        from .webclaw import extract_article
        result = extract_article(url)
        return {
            "content": result.get("content", ""),
            "markdown": result.get("content", ""),
            "links": result.get("links", []),
            "metadata": {
                "title": result.get("title", ""),
                "author": result.get("author", ""),
                "date": result.get("date", ""),
            },
            "source": "webclaw",
            "error": None,
        }
    except Exception as e:
        return {
            "content": "",
            "markdown": "",
            "links": [],
            "error": str(e),
            "source": "webclaw",
        }


def scrape_url(
    url: str,
    page_limit: int = 1,
    only_main_content: bool = True,
    include_html: bool = False,
) -> dict:
    """
    Scrape a URL with self-hosted Firecrawl (or fallback to local scrapers).

    Args:
        url: URL to scrape
        page_limit: Number of pages to crawl (default: 1)
        only_main_content: Only return main content (no nav/footers)
        include_html: Include raw HTML

    Returns:
        dict with keys: content, markdown, links, metadata, source, error
    """
    # Try self-hosted Firecrawl first
    if _is_self_hosted_available():
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{FIRECRAWL_HOST}/v0/scrape",
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
                "source": "firecrawl-self-hosted",
                "error": None,
            }
        except Exception as e:
            # Firecrawl failed, fall through to local scrapers
            pass

    # Fallback 1: Playwright (for JS-heavy pages)
    result = _scrape_with_playwright(url, only_main_content)
    if not result.get("error"):
        return result

    # Fallback 2: Scrapling (for fast CSS extraction)
    result = _scrape_with_scrapling(url)
    if not result.get("error"):
        return result

    # Fallback 3: Webclaw (for article extraction)
    result = _scrape_with_webclaw(url)
    if not result.get("error"):
        return result

    return {
        "content": "",
        "markdown": "",
        "links": [],
        "metadata": {},
        "source": "none",
        "error": "All scraping methods failed. Try installing Playwright: playwright install chromium",
    }


def crawl_url(
    url: str,
    limit: int = 10,
    allow_external: bool = False,
    include_html: bool = False,
) -> dict:
    """
    Crawl a URL with multiple pages (self-hosted Firecrawl).

    Args:
        url: Starting URL
        limit: Max pages to crawl
        allow_external: Allow crawling external domains
        include_html: Include raw HTML

    Returns:
        dict with keys: pages (list), source, error
    """
    # Try self-hosted Firecrawl
    if _is_self_hosted_available():
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{FIRECRAWL_HOST}/v0/crawl",
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

            return {
                "pages": pages,
                "total": len(pages),
                "source": "firecrawl-self-hosted",
                "error": None,
            }
        except Exception as e:
            pass

    # Fallback: Use Webclaw batch crawl
    try:
        from .webclaw import batch_crawl

        # Generate URLs (this is a simplified fallback)
        pages = [{"url": url, "source": "webclaw-fallback", "error": "Crawl limit exceeded"}]
        return {
            "pages": pages,
            "total": 1,
            "source": "webclaw",
            "error": "Self-hosted Firecrawl not available. Using single URL.",
        }
    except Exception:
        return {
            "pages": [],
            "source": "none",
            "error": "Crawl requires self-hosted Firecrawl. Start Firecrawl Docker or set FIRECRAWL_HOST",
        }


def map_url(url: str) -> dict:
    """
    Get all URLs from a website (self-hosted Firecrawl).

    Args:
        url: Website to map

    Returns:
        dict with keys: urls (list), source, error
    """
    if _is_self_hosted_available():
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{FIRECRAWL_HOST}/v0/map",
                    headers=_get_headers(),
                    json={"url": url},
                )
                response.raise_for_status()

            data = response.json()

            return {
                "urls": data.get("urls", []),
                "count": len(data.get("urls", [])),
                "source": "firecrawl-self-hosted",
                "error": None,
            }
        except Exception as e:
            return {
                "urls": [],
                "count": 0,
                "source": "none",
                "error": f"Self-hosted Firecrawl map failed: {e}",
            }

    # Fallback: Use Webclaw to get links from a page
    result = _scrape_with_webclaw(url)
    if result.get("links"):
        return {
            "urls": result.get("links", [])[:50],  # Limit to 50 URLs
            "count": len(result.get("links", [])),
            "source": "webclaw",
            "error": None,
        }

    return {
        "urls": [],
        "count": 0,
        "source": "none",
        "error": "URL mapping requires self-hosted Firecrawl or a page with links",
    }


def batch_scrape(urls: List[str], only_main_content: bool = True) -> dict:
    """
    Scrape multiple URLs in batch (self-hosted or fallback).

    Args:
        urls: List of URLs to scrape
        only_main_content: Only return main content

    Returns:
        dict with keys: results (list), total, source, error
    """
    if _is_self_hosted_available():
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{FIRECRAWL_HOST}/v0/batch/scrape",
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

            return {
                "results": results,
                "total": len(results),
                "source": "firecrawl-self-hosted",
                "error": None,
            }
        except Exception:
            pass

    # Fallback: Scrape each URL individually
    results = []
    for url in urls:
        result = scrape_url(url, only_main_content=only_main_content)
        results.append({
            "url": url,
            "markdown": result.get("markdown", ""),
            "success": bool(result.get("content")),
            "error": result.get("error"),
        })

    return {
        "results": results,
        "total": len(results),
        "source": "local-scrapers",
        "error": None,
    }
