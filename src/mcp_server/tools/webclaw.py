"""Webclaw MCP - Advanced web crawling with configurable extractors."""

from __future__ import annotations

import os
import re
from typing import Optional, List, Dict, Any, Callable

try:
    import httpx
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


WEBCLAW_TIMEOUT = int(os.environ.get("WEBCLAW_TIMEOUT", "30"))


def _extract_with_selectors(html: str, selectors: Dict[str, str]) -> dict:
    """Extract data using CSS selectors."""
    if not BS4_AVAILABLE:
        return {"error": "beautifulsoup4 not installed"}

    soup = BeautifulSoup(html, 'html.parser')
    result = {}

    for key, selector in selectors.items():
        elements = soup.select(selector)
        if len(elements) == 1:
            result[key] = elements[0].get_text(strip=True)
        else:
            result[key] = [e.get_text(strip=True) for e in elements]

    return result


def _extract_schemaorg(html: str) -> dict:
    """Extract Schema.org structured data."""
    if not BS4_AVAILABLE:
        return {}

    soup = BeautifulSoup(html, 'html.parser')

    # Find JSON-LD scripts
    schemas = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            import json
            data = json.loads(script.string)
            schemas.append(data)
        except:
            pass

    return {"structured_data": schemas}


def crawl_with_selectors(
    url: str,
    selectors: Dict[str, str],
    follow_links: bool = False,
    max_depth: int = 1,
) -> dict:
    """
    Crawl URL and extract using CSS selectors.

    Args:
        url: URL to crawl
        selectors: Dict of {field_name: css_selector}
        follow_links: Whether to follow links on page
        max_depth: Maximum crawl depth

    Returns:
        dict with keys: data, links, error
    """
    if not BS4_AVAILABLE:
        return {"data": {}, "links": [], "error": "beautifulsoup4 not installed"}

    try:
        with httpx.Client(timeout=WEBCLAW_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Webclaw/1.0)",
            })
            response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Extract data
        data = _extract_with_selectors(html, selectors)

        # Get links
        links = []
        for a in soup.find_all('a', href=True)[:30]:
            href = a.get('href', '')
            if href.startswith('http') or href.startswith('/'):
                links.append(href)

        return {
            "data": data,
            "links": links,
            "title": soup.title.string if soup.title else "",
            "url": str(response.url),
            "error": None,
        }
    except Exception as e:
        return {"data": {}, "links": [], "error": str(e)}


def extract_article(url: str) -> dict:
    """Extract article content using common patterns."""
    if not BS4_AVAILABLE:
        return {"error": "beautifulsoup4 not installed"}

    article_selectors = [
        'article',
        '[class*=article]',
        '[class*=post]',
        '[class*=entry]',
        'main',
        '[role=main]',
    ]

    try:
        with httpx.Client(timeout=WEBCLAW_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Webclaw/1.0)",
            })
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find article content
        article_content = None
        for selector in article_selectors:
            elem = soup.select_one(selector)
            if elem:
                article_content = elem
                break

        if not article_content:
            article_content = soup.body

        # Extract metadata
        metadata = {
            "title": soup.find('title').get_text(strip=True) if soup.find('title') else "",
            "author": "",
            "date": "",
            "description": "",
        }

        # Try to find author
        for sel in ['[rel=author]', '[class*=author]', '[class*=byline]']:
            author_elem = soup.select_one(sel)
            if author_elem:
                metadata["author"] = author_elem.get_text(strip=True)
                break

        # Try to find date
        for sel in ['time[datetime]', '[class*=date]', '[class*=published]']:
            date_elem = soup.select_one(sel)
            if date_elem:
                if date_elem.name == 'time':
                    metadata["date"] = date_elem.get('datetime', '')
                else:
                    metadata["date"] = date_elem.get_text(strip=True)
                break

        # Try to find description
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            metadata["description"] = desc.get('content', '')

        # Get main content
        paragraphs = article_content.find_all('p') if article_content else []
        content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50)

        return {
            "title": metadata["title"],
            "author": metadata["author"],
            "date": metadata["date"],
            "content": content,
            "description": metadata["description"],
            "url": str(response.url),
            "links": [a.get('href') for a in soup.find_all('a', href=True) if a.get('href', '').startswith('http')][:20],
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


def extract_product(url: str) -> dict:
    """Extract e-commerce product information."""
    if not BS4_AVAILABLE:
        return {"error": "beautifulsoup4 not installed"}

    try:
        with httpx.Client(timeout=WEBCLAW_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Webclaw/1.0)",
            })
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Common product selectors
        title = soup.select_one('h1, [class*=product-title], [class*=title]')
        price = soup.select_one('[class*=price]:not([class*=old]):not([class*=was])')
        description = soup.select_one('[class*=description], [class*=product-info]')
        images = [img.get('src', '') for img in soup.select('[class*=image] img, [class*=gallery] img')[:5]]

        return {
            "title": title.get_text(strip=True) if title else "",
            "price": price.get_text(strip=True) if price else "",
            "description": description.get_text(strip=True)[:1000] if description else "",
            "images": images,
            "url": str(response.url),
            "schema": _extract_schemaorg(response.text),
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


def batch_crawl(urls: List[str], extractor: str = "article") -> dict:
    """
    Crawl multiple URLs.

    Args:
        urls: List of URLs
        extractor: Extractor type ('article', 'product', 'custom')

    Returns:
        dict with keys: results (list), error
    """
    results = []

    for url in urls:
        if extractor == "article":
            result = extract_article(url)
        elif extractor == "product":
            result = extract_product(url)
        else:
            result = {"error": f"Unknown extractor: {extractor}"}

        results.append({
            "url": url,
            "data": result,
        })

    return {"results": results, "total": len(results), "error": None}


def extract_with_regex(html: str, pattern: str, group: int = 0) -> List[str]:
    """Extract using regex pattern."""
    matches = re.findall(pattern, html)
    return [m[group] if isinstance(m, tuple) else m for m in matches]


def find_emails(url: str) -> dict:
    """Find email addresses on a page."""
    try:
        with httpx.Client(timeout=WEBCLAW_TIMEOUT) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Webclaw/1.0)",
            })

        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = list(set(re.findall(email_pattern, response.text)))[:20]

        return {"emails": emails, "count": len(emails), "error": None}
    except Exception as e:
        return {"emails": [], "count": 0, "error": str(e)}


def find_social_links(url: str) -> dict:
    """Find social media links on a page."""
    try:
        with httpx.Client(timeout=WEBCLAW_TIMEOUT) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Webclaw/1.0)",
            })

        soup = BeautifulSoup(response.text, 'html.parser')

        social_patterns = {
            "twitter": r'twitter\.com|	x\.com',
            "linkedin": r'linkedin\.com',
            "facebook": r'facebook\.com',
            "instagram": r'instagram\.com',
            "github": r'github\.com',
            "youtube": r'youtube\.com',
        }

        social_links = {}
        for platform, pattern in social_patterns.items():
            links = [a.get('href', '') for a in soup.find_all('a', href=True)
                     if re.search(pattern, a.get('href', ''), re.I)]
            if links:
                social_links[platform] = list(set(links))[:5]

        return {"social_links": social_links, "error": None}
    except Exception as e:
        return {"social_links": {}, "error": str(e)}