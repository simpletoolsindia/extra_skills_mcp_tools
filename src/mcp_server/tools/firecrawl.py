"""Firecrawl MCP - Optional advanced web scraping.

NOTE: Self-hosted Firecrawl requires significant resources:
- API service: 4 CPU cores, 8GB RAM minimum
- Playwright service: 2 CPU cores, 4GB RAM minimum
- Total: ~6 CPU cores, 12GB RAM

For lightweight servers (Pi5), use the built-in scrapers instead:
- Playwright (already installed) - for JS-heavy pages
- Scrapling - for fast CSS extraction
- Webclaw - for article extraction
"""

from __future__ import annotations

import os
import asyncio
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

# Self-hosted Firecrawl URL
FIRECRAWL_HOST = os.environ.get("FIRECRAWL_HOST", "http://localhost:3002")
FIRECRAWL_TOKEN = os.environ.get("FIRECRAWL_API_TOKEN", "")


def _get_headers() -> dict:
    """Get headers for Firecrawl API."""
    headers = {"Content-Type": "application/json"}
    if FIRECRAWL_TOKEN:
        headers["Authorization"] = f"Bearer {FIRECRAWL_TOKEN}"
    return headers


def _is_firecrawl_available() -> bool:
    """Check if self-hosted Firecrawl is running."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{FIRECRAWL_HOST}/health")
            return response.status_code == 200
    except Exception:
        return False


def _get_resource_info() -> dict:
    """Get recommended scraper based on server resources."""
    return {
        "firecrawl_available": _is_firecrawl_available(),
        "playwright_available": _is_playwright_available(),
        "recommendation": "firecrawl" if _is_firecrawl_available() else "playwright",
        "note": "Firecrawl requires 6 CPU + 12GB RAM. Using lightweight alternatives.",
    }


def _is_playwright_available() -> bool:
    """Check if Playwright is available."""
    try:
        from .playwright_scrape import scrape_dynamic_page
        return True
    except Exception:
        return False


def _scrape_with_playwright(url: str, only_main_content: bool = True) -> dict:
    """Scrape using Playwright (self-hosted, lightweight)."""
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
    """Scrape using Scrapling (self-hosted, fast)."""
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
    """Scrape using Webclaw (self-hosted, article-focused)."""
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
    Scrape a URL using best available scraper.

    Priority: Firecrawl (if available) > Playwright > Scrapling > Webclaw

    For Firecrawl self-hosting (requires 6 CPU + 12GB RAM):
    See: https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md

    Args:
        url: URL to scrape
        page_limit: Number of pages to crawl
        only_main_content: Only return main content
        include_html: Include raw HTML

    Returns:
        dict with keys: content, markdown, links, metadata, source, error
    """
    # Try Firecrawl first (if available)
    if _is_firecrawl_available():
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
        except Exception:
            pass

    # Fallback 1: Playwright (JS rendering)
    result = _scrape_with_playwright(url, only_main_content)
    if not result.get("error"):
        return result

    # Fallback 2: Scrapling (fast CSS)
    result = _scrape_with_scrapling(url)
    if not result.get("error"):
        return result

    # Fallback 3: Webclaw (article extraction)
    result = _scrape_with_webclaw(url)
    if not result.get("error"):
        return result

    return {
        "content": "",
        "markdown": "",
        "links": [],
        "metadata": {},
        "source": "none",
        "error": "All scrapers failed. Install Playwright: playwright install chromium",
        "resource_info": _get_resource_info(),
    }


def crawl_url(
    url: str,
    limit: int = 10,
    allow_external: bool = False,
    include_html: bool = False,
) -> dict:
    """
    Crawl multiple pages.

    For multi-page crawling with Firecrawl:
    1. Self-host Firecrawl (requires 6 CPU + 12GB RAM)
    2. Or use webclaw.batch_crawl for simple site maps
    """
    if _is_firecrawl_available():
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
        except Exception:
            pass

    # Fallback: Use Webclaw for simple crawling
    from .webclaw import crawl_with_selectors

    # Get links from page first
    page_data = scrape_url(url)
    links = page_data.get("links", [])[:limit]

    pages = [{"url": url, "content": page_data.get("content", ""), "source": "local"}]

    return {
        "pages": pages,
        "total": len(pages),
        "source": "local-fallback",
        "error": "Multi-page crawl requires self-hosted Firecrawl. Use webclaw_crawl for single-page with selectors.",
        "resource_info": {
            "firecrawl_required": True,
            "requirements": "6 CPU cores, 12GB RAM",
            "docs": "https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md",
        },
    }


def map_url(url: str) -> dict:
    """
    Get all URLs from a website.

    Self-hosted Firecrawl required for full site mapping.
    """
    if _is_firecrawl_available():
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
            pass

    # Fallback: Get links from homepage
    result = _scrape_with_webclaw(url)
    if result.get("links"):
        return {
            "urls": result.get("links", [])[:50],
            "count": len(result.get("links", [])),
            "source": "webclaw-fallback",
            "error": "Full site mapping requires self-hosted Firecrawl",
            "resource_info": {
                "firecrawl_required": True,
                "requirements": "6 CPU cores, 12GB RAM",
                "docs": "https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md",
            },
        }

    return {
        "urls": [],
        "count": 0,
        "source": "none",
        "error": "URL mapping requires self-hosted Firecrawl",
    }


def batch_scrape(urls: List[str], only_main_content: bool = True) -> dict:
    """Scrape multiple URLs in batch."""
    if _is_firecrawl_available():
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{FIRECRAWL_HOST}/v0/batch/scrape",
                    headers=_get_headers(),
                    json={"urls": urls, "onlyMainContent": only_main_content},
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

    # Fallback: Scrape individually
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
        "successful": sum(1 for r in results if r["success"]),
        "source": "local-scrapers",
        "error": None,
    }


def get_scraper_status() -> dict:
    """Get status of all available scrapers."""
    return {
        "firecrawl": {
            "available": _is_firecrawl_available(),
            "host": FIRECRAWL_HOST,
            "optional": True,
            "requirements": "6 CPU cores, 12GB RAM",
            "install": "https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md",
        },
        "playwright": {
            "available": _is_playwright_available(),
            "optional": False,
            "requirements": "Default (lightweight)",
            "install": "playwright install chromium",
        },
        "scrapling": {
            "available": True,
            "optional": False,
            "requirements": "Default (lightweight)",
            "install": "pip install scrapling",
        },
        "webclaw": {
            "available": True,
            "optional": False,
            "requirements": "Default (lightweight)",
            "install": "Included",
        },
        "active_scraper": "playwright" if _is_playwright_available() else "scrapling",
    }
