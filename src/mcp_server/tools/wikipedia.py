"""Wikipedia MCP integration - Search and fetch Wikipedia articles."""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_REST = "https://en.wikipedia.org/api/rest_v1"


def search_wikipedia(query: str, limit: int = 10) -> dict:
    """
    Search Wikipedia for articles.

    Args:
        query: Search query
        limit: Maximum results (default: 10)

    Returns:
        dict with keys: results (list), error
    """
    if not HTTpx_AVAILABLE:
        return {"results": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                WIKIPEDIA_API,
                params={
                    "action": "opensearch",
                    "search": query,
                    "limit": limit,
                    "namespace": 0,
                    "format": "json",
                },
            )
            response.raise_for_status()

        data = response.json()
        titles = data.get("1", [])
        snippets = data.get("2", [])
        links = data.get("3", [])

        results = []
        for i, title in enumerate(titles):
            results.append({
                "title": title,
                "snippet": snippets[i] if i < len(snippets) else "",
                "url": links[i] if i < len(links) else "",
            })

        return {"results": results, "error": None}

    except Exception as e:
        return {"results": [], "error": str(e)}


def get_article(title: str, extract_length: int = 2000) -> dict:
    """
    Get Wikipedia article content.

    Args:
        title: Article title (URL-encoded or raw)
        extract_length: Maximum characters to extract

    Returns:
        dict with keys: title, extract, url, categories, error
    """
    if not HTTpx_AVAILABLE:
        return {"title": "", "extract": "", "url": "", "categories": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            # Use REST API for summary
            response = client.get(
                f"{WIKIPEDIA_REST}/page/summary/{title.replace(' ', '_')}",
            )
            response.raise_for_status()

        data = response.json()

        return {
            "title": data.get("title", ""),
            "extract": data.get("extract", "")[:extract_length],
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "thumbnail": data.get("thumbnail", {}).get("source", ""),
            "description": data.get("description", ""),
            "categories": list(data.get("categories", {}).keys()) if isinstance(data.get("categories"), dict) else [],
            "error": None,
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"title": "", "extract": "", "url": "", "categories": [], "error": "Article not found"}
        return {"title": "", "extract": "", "url": "", "categories": [], "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"title": "", "extract": "", "url": "", "categories": [], "error": str(e)}


def get_article_html(title: str) -> dict:
    """
    Get full Wikipedia article HTML.

    Args:
        title: Article title

    Returns:
        dict with keys: html, error
    """
    if not HTTpx_AVAILABLE:
        return {"html": "", "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{WIKIPEDIA_REST}/page/html/{title.replace(' ', '_')}",
            )
            response.raise_for_status()

        return {"html": response.text, "error": None}

    except Exception as e:
        return {"html": "", "error": str(e)}


def get_related_articles(title: str, limit: int = 10) -> dict:
    """
    Get articles related to a Wikipedia article.

    Args:
        title: Article title
        limit: Maximum results

    Returns:
        dict with keys: articles (list), error
    """
    if not HTTpx_AVAILABLE:
        return {"articles": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{WIKIPEDIA_REST}/page/related/{title.replace(' ', '_')}",
            )
            response.raise_for_status()

        data = response.json()
        pages = data.get("pages", [])[:limit]

        articles = []
        for page in pages:
            articles.append({
                "title": page.get("title", ""),
                "description": page.get("description", ""),
                "thumbnail": page.get("thumbnail", {}).get("source", ""),
                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
            })

        return {"articles": articles, "error": None}

    except Exception as e:
        return {"articles": [], "error": str(e)}


def get_wiki_search(query: str, limit: int = 20) -> dict:
    """
    Full Wikipedia search with more options.

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        dict with keys: pages (list), error
    """
    if not HTTpx_AVAILABLE:
        return {"pages": [], "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                WIKIPEDIA_API,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": limit,
                    "format": "json",
                },
            )
            response.raise_for_status()

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        pages = []
        for result in search_results:
            pages.append({
                "title": result.get("title", ""),
                "pageid": result.get("pageid", 0),
                "snippet": result.get("snippet", ""),
                "wordcount": result.get("wordcount", 0),
                "size": result.get("size", 0),
                "url": f"https://en.wikipedia.org/wiki/{result.get('title', '').replace(' ', '_')}",
            })

        return {"pages": pages, "error": None}

    except Exception as e:
        return {"pages": [], "error": str(e)}