"""Freedium article scraping - Medium paywall bypass mirror."""

from __future__ import annotations

from typing import Optional
from ..utils.html_processor import fetch_and_extract


# Try to use scrapling for fast CSS extraction
try:
    import scrapling
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False


def scrape_freedium(url: str, max_length: int = 20000) -> dict:
    """
    Scrape a Freedium article and extract structured content.

    Args:
        url: Freedium URL (e.g., https://freedium-mirror.cfd/ARTICLE_ID)
        max_length: Maximum characters of text to return

    Returns:
        dict with keys: title, author, publication, date, content, tags, url, error
    """
    # Normalize URL - add domain if just path provided
    if not url.startswith("http"):
        url = f"https://freedium-mirror.cfd{url}"

    # First fetch the page
    result = fetch_and_extract(url, max_length=max_length + 5000)

    if result.get("error"):
        return {
            "title": "",
            "author": "",
            "publication": "",
            "date": "",
            "content": "",
            "tags": [],
            "url": url,
            "error": result["error"],
        }

    html = None
    try:
        import httpx
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/1.0)",
            })
            html = response.text
    except Exception:
        pass

    if not html:
        return {
            "title": result.get("title", ""),
            "author": "",
            "publication": "",
            "date": "",
            "content": result.get("text", ""),
            "tags": [],
            "url": url,
            "error": None,
        }

    # Extract structured data using scrapling
    if SCRAPLING_AVAILABLE:
        try:
            page = scrapling.parse(html)

            # Title
            title = ""
            title_elem = page.css_first("h1")
            if not title_elem:
                title_elem = page.css_first("[class*=article-title], .article-header h1")
            if title_elem:
                title = title_elem.text(strip=True)

            # Author
            author = ""
            author_elem = page.css_first("[class*=author], [rel='author']")
            if author_elem:
                author = author_elem.text(strip=True)

            # Publication
            publication = ""
            pub_elem = page.css_first("[class*=publication], [class*=publication-name]")
            if pub_elem:
                publication = pub_elem.text(strip=True)

            # Date
            date = ""
            date_elem = page.css_first("time, [class*=date], [class*=published]")
            if date_elem:
                date = date_elem.text(strip=True)
                if date_elem.tag == "time":
                    date = date_elem.get("datetime", date)

            # Main content - look for article body
            content = ""
            content_selectors = [
                "article [class*=body]",
                "[class*=article-content]",
                "[class*=main-content]",
                ".article-body",
                "article",
            ]
            for selector in content_selectors:
                elem = page.css_first(selector)
                if elem:
                    content = elem.text(strip=True, separator="\n")
                    if len(content) > 100:  # Valid content found
                        break

            # Tags
            tags = []
            for tag in page.css("[class*=tag], a[href*='/tag/']")[:20]:
                tag_text = tag.text(strip=True)
                if tag_text and not tag_text.startswith("#"):
                    tags.append(tag_text)

            return {
                "title": title or result.get("title", ""),
                "author": author,
                "publication": publication,
                "date": date,
                "content": content[:max_length] if content else result.get("text", "")[:max_length],
                "tags": tags,
                "url": url,
                "error": None,
            }
        except Exception as e:
            # Fallback to basic extraction
            pass

    # Fallback to basic result
    return {
        "title": result.get("title", ""),
        "author": "",
        "publication": "",
        "date": "",
        "content": result.get("text", "")[:max_length],
        "tags": [],
        "url": url,
        "error": None,
    }


def list_freedium_articles(url: str = "https://freedium-mirror.cfd/", limit: int = 20) -> dict:
    """
    List articles on Freedium homepage or category page.

    Args:
        url: Freedium URL to scrape (default: homepage)
        limit: Maximum number of articles to return

    Returns:
        dict with keys: articles (list), url, error
    """
    try:
        import httpx
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/1.0)",
            })
            html = response.text
    except Exception as e:
        return {
            "articles": [],
            "url": url,
            "error": str(e),
        }

    if SCRAPLING_AVAILABLE:
        try:
            page = scrapling.parse(html)
            articles = []

            # Find article cards - look for common patterns
            article_selectors = [
                "article[class*=card]",
                "[class*=article-card]",
                ".article-item",
                "a[href*='/v/']",  # Freedium article URLs
            ]

            for selector in article_selectors:
                items = page.css(selector)[:limit]
                if items:
                    for item in items:
                        link = item.css_first("a[href]") if item.tag != "a" else item
                        href = link.get("href", "") if link else ""

                        if "/v/" in href or "/926" in href:  # Article URLs
                            title_elem = item.css_first("h1, h2, h3, [class*=title]")
                            title = title_elem.text(strip=True) if title_elem else ""

                            pub_elem = item.css_first("[class*=publication], [class*=pub-name]")
                            publication = pub_elem.text(strip=True) if pub_elem else ""

                            date_elem = item.css_first("time, [class*=date]")
                            date = date_elem.text(strip=True) if date_elem else ""

                            free_elem = item.css_first("[class*=free]")
                            is_free = "Yes" if free_elem and "yes" in free_elem.text(strip=True).lower() else "No"

                            read_time_elem = item.css_first("[class*=read], [class*=time]")
                            read_time = read_time_elem.text(strip=True) if read_time_elem else ""

                            # Normalize URL
                            if href and not href.startswith("http"):
                                href = f"https://freedium-mirror.cfd{href}"

                            if title:
                                articles.append({
                                    "title": title,
                                    "url": href,
                                    "publication": publication,
                                    "date": date,
                                    "is_free": is_free,
                                    "read_time": read_time,
                                })

                    if articles:
                        break

            return {
                "articles": articles[:limit],
                "url": url,
                "error": None,
            }
        except Exception:
            pass

    # Fallback: return empty with error
    return {
        "articles": [],
        "url": url,
        "error": "Failed to extract articles. Try using scrape_dynamic for JS-rendered content.",
    }