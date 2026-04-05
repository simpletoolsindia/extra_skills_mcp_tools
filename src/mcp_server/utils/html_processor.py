"""HTML fetching and content extraction utilities."""

from __future__ import annotations

import httpx
from readability import Document
from bs4 import BeautifulSoup


def fetch_and_extract(url: str, max_length: int = 8000) -> dict:
    """
    Fetch a URL and extract clean, LLM-friendly content.

    Returns:
        dict with keys: title, text, url, links, error (if any)
    """
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; MCP-Server/1.0; "
                    "+https://github.com/local-llm/mcp-server)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            })
            response.raise_for_status()

        doc = Document(response.text)

        # Extract title
        title = doc.title() or ""

        # Extract main content with BeautifulSoup for link collection
        soup = BeautifulSoup(doc.summary(), "html.parser")

        # Get text content
        text = soup.get_text(separator="\n", strip=True)

        # Collapse excess whitespace
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        # Collect links
        all_soup = BeautifulSoup(response.text, "html.parser")
        links = [
            {"text": a.get_text(strip=True)[:100], "href": a.get("href", "")}
            for a in all_soup.find_all("a", href=True)
            if a.get_text(strip=True)
        ][:20]  # Limit to first 20 links

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated]"

        return {
            "title": title,
            "text": text,
            "url": str(response.url),
            "links": links,
            "error": None,
        }

    except httpx.TimeoutException:
        return {"title": "", "text": "", "url": url, "links": [], "error": "Request timed out"}
    except httpx.HTTPStatusError as e:
        return {"title": "", "text": "", "url": url, "links": [], "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"title": "", "text": "", "url": url, "links": [], "error": str(e)}
