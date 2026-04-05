"""Native SearXNG integration with enhanced search capabilities."""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False


SEARXNG_BASE_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8888")
SEARXNG_TIMEOUT = float(os.environ.get("SEARXNG_TIMEOUT", "15"))


def search(
    query: str,
    limit: int = 10,
    categories: Optional[List[str]] = None,
    engines: Optional[List[str]] = None,
    time_range: Optional[str] = None,
    language: str = "en",
) -> dict:
    """
    Search via SearXNG with advanced options.

    Args:
        query: Search query string
        limit: Number of results (max 50)
        categories: Filter by categories (e.g., ['news', 'web', 'images'])
        engines: Use specific engines (e.g., ['google', 'duckduckgo'])
        time_range: Time filter ('day', 'week', 'month', 'year')
        language: Language code (default: 'en')

    Returns:
        dict with keys: results (list), error, engines_used, query_time
    """
    if not HTTpx_AVAILABLE:
        return {"results": [], "error": "httpx not installed", "engines_used": [], "query_time": 0}

    limit = min(max(1, limit), 50)
    params = {
        "q": query,
        "format": "json",
        "engines": ",".join(engines) if engines else "",
        "categories": ",".join(categories) if categories else "",
        "time_range": time_range or "",
        "language": language,
    }
    # Remove empty params
    params = {k: v for k, v in params.items() if v}

    try:
        import time
        start = time.time()

        with httpx.Client(timeout=SEARXNG_TIMEOUT, follow_redirects=True) as client:
            response = client.get(
                f"{SEARXNG_BASE_URL}/search",
                params=params,
                headers={
                    "X-Forwarded-For": "127.0.0.1",
                    "User-Agent": "MCP-Server/1.0 (Agentic Web Search)",
                },
            )

        query_time = time.time() - start

        if response.status_code == 403:
            return {
                "results": [],
                "error": "SearXNG returned 403. Ensure limiter is disabled in settings.yml",
                "engines_used": [],
                "query_time": query_time,
            }
        response.raise_for_status()

        data = response.json()
        results = []

        for item in data.get("results", [])[:limit]:
            # Extract image if available
            img_src = ""
            if "img" in item:
                img_src = item.get("img", "")
            elif "thumbnail" in item:
                img_src = item.get("thumbnail", "")

            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "engine": item.get("engine", ""),
                "thumbnail": img_src,
                "published": item.get("published", ""),
            })

        return {
            "results": results,
            "error": None,
            "engines_used": list(set(r["engine"] for r in results)),
            "query_time": round(query_time, 2),
        }

    except httpx.ConnectError:
        return {
            "results": [],
            "error": f"Cannot connect to SearXNG at {SEARXNG_BASE_URL}. Start with: docker run -d -p 8888:8080 --name searxng searxng/searxng",
            "engines_used": [],
            "query_time": 0,
        }
    except httpx.TimeoutException:
        return {"results": [], "error": "Search timed out", "engines_used": [], "query_time": SEARXNG_TIMEOUT}
    except Exception as e:
        return {"results": [], "error": str(e), "engines_used": [], "query_time": 0}


def search_images(query: str, limit: int = 10) -> dict:
    """Search for images via SearXNG."""
    return search(query, limit=limit, categories=["images"])


def search_news(query: str, limit: int = 10, time_range: Optional[str] = None) -> dict:
    """Search for news via SearXNG."""
    return search(query, limit=limit, categories=["news"], time_range=time_range or "month")


def search_videos(query: str, limit: int = 10) -> dict:
    """Search for videos via SearXNG."""
    return search(query, limit=limit, categories=["videos"])


def search_scientific(query: str, limit: int = 10) -> dict:
    """Search for scientific/academic content via SearXNG."""
    return search(query, limit=limit, categories=["science"])


def get_instance_stats() -> dict:
    """Get SearXNG instance statistics."""
    if not HTTpx_AVAILABLE:
        return {"error": "httpx not installed"}

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{SEARXNG_BASE_URL}/stats")
            response.raise_for_status()
        return {"stats": response.json(), "error": None}
    except Exception as e:
        return {"error": str(e)}


def health_check() -> dict:
    """Check if SearXNG is running and healthy."""
    if not HTTpx_AVAILABLE:
        return {"status": "unavailable", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{SEARXNG_BASE_URL}/search?q=test&format=json")
            if response.status_code == 200:
                return {"status": "healthy", "error": None}
            return {"status": "degraded", "error": f"HTTP {response.status_code}"}
    except httpx.ConnectError:
        return {"status": "offline", "error": "Cannot connect to SearXNG"}
    except Exception as e:
        return {"status": "error", "error": str(e)}