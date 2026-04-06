"""Token-optimized web content fetching with structured extraction."""

from __future__ import annotations

import httpx
from typing import Optional

from ..utils.content_extractor import (
    extract_main_content,
    extract_structured_from_html,
    estimate_tokens,
    strip_html_noise,
)


def fetch_web_content(url: str, max_tokens: int = 4000) -> dict:
    """
    Fetch a URL and extract clean, LLM-friendly content.
    Optimized to minimize token usage while preserving meaning.

    Args:
        url: The URL to fetch
        max_tokens: Maximum tokens to return (default: 4000)

    Returns:
        dict with keys: title, text, url, links, tokens_used, error
    """
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; MCP-Server/2.0; "
                    "+https://github.com/local-llm/mcp-server)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            })
            response.raise_for_status()

        html = response.text

        # Extract optimized content
        result = extract_main_content(url, html, max_tokens=max_tokens)

        return {
            "title": result.get("title", ""),
            "text": result.get("text", ""),
            "url": result.get("url", url),
            "links": result.get("links", []),
            "tokens_used": result.get("tokens_used", 0),
            "truncated": result.get("truncated", False),
            "error": result.get("error"),
        }

    except httpx.TimeoutException:
        return {
            "title": "",
            "text": "",
            "url": url,
            "links": [],
            "tokens_used": 0,
            "truncated": False,
            "error": "Request timed out",
        }
    except httpx.HTTPStatusError as e:
        return {
            "title": "",
            "text": "",
            "url": url,
            "links": [],
            "tokens_used": 0,
            "truncated": False,
            "error": f"HTTP {e.response.status_code}",
        }
    except Exception as e:
        return {
            "title": "",
            "text": "",
            "url": url,
            "links": [],
            "tokens_used": 0,
            "truncated": False,
            "error": str(e),
        }


def fetch_structured(
    url: str,
    extraction_type: str = "article",
    max_tokens: int = 2000,
) -> dict:
    """
    Fetch URL and extract structured data (article, product, table, links).
    Most token-efficient for specific data extraction.

    Args:
        url: URL to fetch
        extraction_type: 'article', 'product', 'table', or 'links'
        max_tokens: Max tokens for content field

    Returns:
        dict with extracted structured data
    """
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/2.0)",
                "Accept": "text/html,application/xhtml+xml",
            })
            response.raise_for_status()

        html = response.text

        # Extract based on type
        result = extract_structured_from_html(html, extraction_type)

        # Add URL
        result["url"] = str(response.url)

        # Truncate content if needed
        if "content" in result and result["content"]:
            tokens = estimate_tokens(result["content"])
            if tokens > max_tokens:
                result["content"] = result["content"][:max_tokens * 4] + "\n\n[Truncated]"
                result["truncated"] = True
            else:
                result["truncated"] = False
        else:
            result["truncated"] = False

        result["error"] = None
        return result

    except Exception as e:
        return {"error": str(e), "url": url}


def fetch_with_selectors(
    url: str,
    selectors: dict,
    max_tokens: int = 2000,
) -> dict:
    """
    Fetch URL and extract using CSS selectors.
    Most efficient when you know the page structure.

    Args:
        url: URL to fetch
        selectors: Dict of {field_name: css_selector}
        max_tokens: Max tokens for any text field

    Returns:
        dict with extracted data
    """
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/2.0)",
                "Accept": "text/html,application/xhtml+xml",
            })
            response.raise_for_status()

        html = response.text

        # Strip noise
        cleaned_html = strip_html_noise(html)

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(cleaned_html, "html.parser")

        result = {"url": str(response.url)}
        total_text = []

        for field, selector in selectors.items():
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                result[field] = text
                total_text.append(text)
            else:
                result[field] = ""

        # Estimate total tokens
        combined_text = " ".join(total_text)
        tokens = estimate_tokens(combined_text)

        return {
            "data": result,
            "url": str(response.url),
            "tokens_used": tokens,
            "truncated": tokens > max_tokens,
            "error": None,
        }

    except Exception as e:
        return {"data": {}, "url": url, "error": str(e)}


def quick_fetch(url: str, max_tokens: int = 1500) -> dict:
    """
    Ultra-fast fetch for quick lookups.
    Returns minimal data optimized for speed and token efficiency.

    Args:
        url: URL to fetch
        max_tokens: Max tokens (default: 1500 for quick response)

    Returns:
        dict with: title, summary, url, error
    """
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/2.0)",
            })
            response.raise_for_status()

        html = response.text

        # Fast title extraction
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else ""

        # Get meta description as quick summary
        desc = soup.find("meta", attrs={"name": "description"})
        description = desc.get("content", "") if desc else ""

        # Get first paragraph as summary
        from ..utils.content_extractor import strip_html_noise
        cleaned = strip_html_noise(html)
        soup2 = BeautifulSoup(cleaned, "html.parser")
        first_p = soup2.find("p")
        summary = first_p.get_text(strip=True) if first_p else description

        # Truncate summary
        if len(summary) > max_tokens * 4:
            summary = summary[:max_tokens * 4].rsplit(".", 1)[0] + "."

        return {
            "title": title_text,
            "summary": summary,
            "url": str(response.url),
            "tokens_used": estimate_tokens(summary),
            "error": None,
        }

    except Exception as e:
        return {"title": "", "summary": "", "url": url, "error": str(e)}
