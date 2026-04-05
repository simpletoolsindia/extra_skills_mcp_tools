"""Web content fetching and extraction tool."""

from __future__ import annotations

from ..utils.html_processor import fetch_and_extract


def fetch_web_content(url: str, max_length: int = 8000) -> dict:
    """
    Fetch a URL and extract clean, LLM-friendly content.

    Args:
        url: The URL to fetch
        max_length: Maximum characters of text to return

    Returns:
        dict with keys: title, text, url, links, error
    """
    return fetch_and_extract(url, max_length)
