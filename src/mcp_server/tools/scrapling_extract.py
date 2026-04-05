"""Scrapling-based content extraction for structured data scraping."""

from __future__ import annotations

from typing import Optional, List, Dict, Any

try:
    import scrapling
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False


class ProductExtractor:
    """Extraction patterns for common content types."""

    @staticmethod
    def ecommerce_product(html: str) -> dict:
        """Extract product info from e-commerce pages."""
        if not SCRAPLING_AVAILABLE:
            return {"error": "Scrapling not installed"}

        try:
            page = scrapling.parse(html)
            return {
                "title": page.css_first("h1").text(strip=True) if page.css_first("h1") else "",
                "price": page.css_first("[class*=price], [id*=price], .product-price").text(strip=True) or "",
                "description": page.css_first("[class*=description], [id*=description]").text(strip=True) or "",
                "images": [img.get("src", "") for img in page.css("[class*=image] img") if img.get("src")][:5],
                "rating": page.css_first("[class*=rating]").text(strip=True) or "",
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def article(html: str) -> dict:
        """Extract article content."""
        if not SCRAPLING_AVAILABLE:
            return {"error": "Scrapling not installed"}

        try:
            page = scrapling.parse(html)
            return {
                "title": page.css_first("h1, article h2").text(strip=True) or "",
                "author": page.css_first("[class*=author], [class*=byline]").text(strip=True) or "",
                "date": page.css_first("time, [class*=date]").text(strip=True) or "",
                "content": page.css_first("article, [class*=content], main").text(strip=True) or "",
                "images": [img.get("src", "") for img in page.css("article img") if img.get("src")][:3],
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def table_rows(html: str, selector: str = "table") -> List[Dict[str, Any]]:
        """Extract table data as list of dicts."""
        if not SCRAPLING_AVAILABLE:
            return [{"error": "Scrapling not installed"}]

        try:
            page = scrapling.parse(html)
            table = page.css_first(selector)
            if not table:
                return []

            headers = [th.text(strip=True) for th in table.css("thead th")]
            if not headers:
                # Use first row as headers
                first_row = table.css_first("tr")
                if first_row:
                    headers = [td.text(strip=True) for td in first_row.css("td")]

            rows = []
            for tr in table.css("tbody tr")[:50]:  # Limit to 50 rows
                cells = [td.text(strip=True) for td in tr.css("td")]
                if headers and len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                elif cells:
                    rows.append({"data": cells})

            return rows
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    def links_by_pattern(html: str, pattern: str) -> List[Dict[str, str]]:
        """Extract links matching a CSS selector pattern."""
        if not SCRAPLING_AVAILABLE:
            return [{"error": "Scrapling not installed"}]

        try:
            page = scrapling.parse(html)
            links = []
            for a in page.css(pattern)[:50]:
                href = a.get("href", "")
                text = a.text(strip=True)
                if href and text:
                    links.append({"text": text[:100], "href": href})
            return links
        except Exception as e:
            return [{"error": str(e)}]


def extract_structured(
    html: str,
    extraction_type: str = "article",
    selector: Optional[str] = None,
    custom_selector: Optional[str] = None,
) -> dict:
    """
    Extract structured data from HTML using scrapling.

    Args:
        html: Raw HTML content
        extraction_type: Type of extraction - 'article', 'product', 'table', 'links'
        selector: CSS selector to target specific element
        custom_selector: Custom CSS selector for links pattern

    Returns:
        dict with extracted structured data
    """
    if not SCRAPLING_AVAILABLE:
        return {
            "error": "scrapling not installed. Run: pip install scrapling",
            "data": {},
        }

    if selector:
        try:
            page = scrapling.parse(html)
            target = page.css_first(selector)
            if target:
                return {
                    "text": target.text(strip=True),
                    "html": target.html,
                    "error": None,
                }
        except Exception as e:
            return {"text": "", "html": "", "error": str(e)}

    extractor = ProductExtractor()
    methods = {
        "article": extractor.article,
        "product": extractor.ecommerce_product,
        "table": lambda h: {"rows": extractor.table_rows(h, selector or "table")},
        "links": lambda h: {"links": extractor.links_by_pattern(h, custom_selector or "a")},
    }

    method = methods.get(extraction_type, extractor.article)
    result = method(html)

    # Clean up None values
    return {k: v for k, v in result.items() if v is not None}