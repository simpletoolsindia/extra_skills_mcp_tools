"""Web search tool via local SearXNG instance."""

from __future__ import annotations

import os
import httpx


SEARXNG_BASE_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8888")


def web_search(query: str, limit: int = 5) -> dict:
    """
    Search the web via local SearXNG.

    Args:
        query: Search query string
        limit: Number of results to return (max 20)

    Returns:
        dict with keys: results (list), error (str or None)
    """
    limit = min(max(1, limit), 20)

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{SEARXNG_BASE_URL}/search",
                params={
                    "q": query,
                    "format": "json",
                    "language": "en",
                },
                headers={
                    # Required by SearXNG bot detection when running behind Docker/ports
                    "X-Forwarded-For": "127.0.0.1",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0",
                },
            )
            if response.status_code == 403:
                return {
                    "results": [],
                    "error": (
                        "SearXNG returned 403. Ensure SearXNG is running with "
                        "JSON format enabled (search.formats includes json) and "
                        "limiter: false in settings.yml. See README.md."
                    ),
                }
            response.raise_for_status()

        data = response.json()

        results = []
        for item in data.get("results", [])[:limit]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "engine": item.get("engine", ""),
            })

        return {"results": results, "error": None}

    except httpx.ConnectError:
        return {
            "results": [],
            "error": (
                f"Cannot connect to SearXNG at {SEARXNG_BASE_URL}. "
                "Ensure SearXNG is running. See README.md for setup instructions."
            ),
        }
    except httpx.TimeoutException:
        return {"results": [], "error": "Search request timed out"}
    except Exception as e:
        return {"results": [], "error": str(e)}
