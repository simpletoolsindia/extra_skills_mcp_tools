"""Content extraction utilities with token optimization for LLM input."""

from __future__ import annotations

import re
from typing import Optional
from bs4 import BeautifulSoup
from readability import Document


# Token estimation (rough: 4 chars per token for English)
CHARS_PER_TOKEN = 4

# Tags to remove for cleaner content
REMOVE_TAGS = [
    "script", "style", "nav", "footer", "header", "aside",
    "noscript", "iframe", "form", "button", "input",
    "[class*=sidebar]", "[class*=nav]", "[class*=menu]",
    "[class*=footer]", "[class*=header]", "[class*=cookie]",
    "[class*=banner]", "[class*=advertisement]", "[class*=social]",
]

# Tags to preserve structure
PRESERVE_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "tr", "code", "pre", "blockquote"]


def estimate_tokens(text: str) -> int:
    """Estimate token count for text."""
    return len(text) // CHARS_PER_TOKEN


def truncate_at_token_limit(text: str, max_tokens: int = 4000) -> str:
    """
    Truncate text at token boundary without summarization.
    Cuts at sentence boundary to preserve meaning.
    """
    max_chars = max_tokens * CHARS_PER_TOKEN

    if len(text) <= max_chars:
        return text

    # Find sentence boundaries
    truncated = text[:max_chars]

    # Try to cut at sentence end
    sentence_ends = re.findall(r'[.!?]+\s', truncated)
    if sentence_ends:
        last_cut = truncated.rfind(sentence_ends[-1]) + len(sentence_ends[-1])
        return truncated[:last_cut] + "\n\n[Content truncated at token limit]"

    # Fallback: cut at last paragraph
    last_newline = truncated.rfind('\n\n')
    if last_newline > max_chars // 2:
        return truncated[:last_newline] + "\n\n[Content truncated at token limit]"

    return truncated + "\n\n[Content truncated at token limit]"


def strip_html_noise(html: str) -> str:
    """
    Remove script, style, nav, footer, and other noise tags.
    This is more aggressive than readability for LLM optimization.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style tags entirely
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Remove header, footer, aside, nav
    for tag in soup(["header", "footer", "aside", "nav"]):
        tag.decompose()

    # Remove common noise classes/ids
    noise_patterns = [
        "cookie", "banner", "advertisement", "sidebar",
        "social", "share", "comment", "related",
    ]

    for pattern in noise_patterns:
        for elem in soup.find_all(class_=re.compile(pattern, re.I)):
            elem.decompose()
        for elem in soup.find_all(id=re.compile(pattern, re.I)):
            elem.decompose()

    return str(soup)


def html_to_clean_markdown(html: str) -> str:
    """
    Convert HTML to clean Markdown for LLM consumption.
    Preserves structure while removing markup noise.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise tags first
    html = strip_html_noise(html)
    soup = BeautifulSoup(html, "html.parser")

    markdown_parts = []

    def get_text(elem, preserve_structure: bool = True) -> str:
        """Extract text with optional structure preservation."""
        if not elem:
            return ""

        text = elem.get_text(separator="\n", strip=True)
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return text

    # Process headings
    for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        for elem in soup.find_all(tag):
            text = elem.get_text(strip=True)
            if text:
                prefix = "#" * int(tag[1])
                markdown_parts.append(f"{prefix} {text}\n")

    # Process paragraphs
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if text and len(text) > 20:  # Filter short fragments
            markdown_parts.append(f"{text}\n")

    # Process lists
    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            text = li.get_text(strip=True)
            if text:
                markdown_parts.append(f"- {text}")
    for ol in soup.find_all("ol"):
        for i, li in enumerate(ol.find_all("li", recursive=False), 1):
            text = li.get_text(strip=True)
            if text:
                markdown_parts.append(f"{i}. {text}")

    # Process code blocks
    for pre in soup.find_all("pre"):
        code = pre.find("code")
        if code:
            text = code.get_text()
            markdown_parts.append(f"```\n{text}\n```\n")

    # Process blockquotes
    for blockquote in soup.find_all("blockquote"):
        text = blockquote.get_text(strip=True)
        if text:
            markdown_parts.append(f"> {text}\n")

    # Process tables
    for table in soup.find_all("table"):
        markdown_parts.append(_table_to_markdown(table))

    # Process remaining text content (if no better structure found)
    if not markdown_parts:
        text = soup.get_text(separator="\n", strip=True)
        markdown_parts.append(text)

    result = "\n\n".join(part for part in markdown_parts if part.strip())

    # Clean up excessive newlines
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def _table_to_markdown(table) -> str:
    """Convert HTML table to Markdown table."""
    rows = table.find_all("tr")
    if not rows:
        return ""

    lines = []

    # Process header
    header_row = rows[0]
    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

    if headers:
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Process data rows
        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
            if cells:
                lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def extract_main_content(url: str, html: str, max_tokens: int = 4000) -> dict:
    """
    Extract clean, LLM-optimized content from HTML.

    Uses Readability for initial extraction, then applies aggressive
    cleaning and markdown conversion for optimal token usage.

    Returns:
        dict with: title, text, markdown, url, links, error, tokens_used
    """
    try:
        # Use Readability for main content extraction
        doc = Document(html)
        title = doc.title() or ""

        # Get readability summary
        readability_html = doc.summary()

        # Strip noise tags
        cleaned_html = strip_html_noise(readability_html)

        # Convert to markdown
        markdown = html_to_clean_markdown(cleaned_html)

        # Estimate tokens used
        tokens_used = estimate_tokens(markdown)

        # Truncate if needed
        if tokens_used > max_tokens:
            markdown = truncate_at_token_limit(markdown, max_tokens)
            tokens_used = max_tokens

        # Extract links for reference
        all_soup = BeautifulSoup(html, "html.parser")
        links = [
            {"text": a.get_text(strip=True)[:100], "href": a.get("href", "")}
            for a in all_soup.find_all("a", href=True)
            if a.get_text(strip=True)
        ][:15]

        return {
            "title": title,
            "text": markdown,  # Markdown is preferred for LLMs
            "markdown": markdown,
            "url": url,
            "links": links,
            "tokens_used": tokens_used,
            "truncated": tokens_used >= max_tokens,
            "error": None,
        }

    except Exception as e:
        return {
            "title": "",
            "text": "",
            "markdown": "",
            "url": url,
            "links": [],
            "tokens_used": 0,
            "truncated": False,
            "error": str(e),
        }


def extract_structured_from_html(
    html: str,
    extraction_type: str = "article",
    schema: Optional[dict] = None,
) -> dict:
    """
    Extract structured data from HTML based on type or custom schema.

    Args:
        html: Raw HTML content
        extraction_type: Type of extraction - 'article', 'product', 'table', 'links'
        schema: Optional custom schema for extraction

    Returns:
        dict with extracted fields matching the schema
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise first
    html = strip_html_noise(html)
    soup = BeautifulSoup(html, "html.parser")

    if extraction_type == "article":
        return _extract_article(soup)
    elif extraction_type == "product":
        return _extract_product(soup)
    elif extraction_type == "table":
        return _extract_tables(soup)
    elif extraction_type == "links":
        return _extract_links(soup)
    elif schema:
        return _extract_with_schema(soup, schema)
    else:
        return _extract_article(soup)


def _extract_article(soup: BeautifulSoup) -> dict:
    """Extract article content with metadata."""
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""

    # Get main content
    content_elem = soup.find("article") or soup.find("main") or soup.find("body")

    if content_elem:
        # Extract paragraphs
        paragraphs = []
        for p in content_elem.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 50:  # Filter short fragments
                paragraphs.append(text)

        content = "\n\n".join(paragraphs)
    else:
        content = ""

    # Extract metadata
    metadata = {
        "author": "",
        "date": "",
        "description": "",
    }

    # Author
    for sel in ['[rel="author"]', '[class*="author"]', '[class*="byline"]']:
        elem = soup.select_one(sel)
        if elem:
            metadata["author"] = elem.get_text(strip=True)
            break

    # Date
    time_elem = soup.find("time")
    if time_elem:
        metadata["date"] = time_elem.get("datetime", time_elem.get_text(strip=True))

    # Description
    desc = soup.find("meta", attrs={"name": "description"})
    if desc:
        metadata["description"] = desc.get("content", "")

    return {
        "title": title_text,
        "author": metadata["author"],
        "date": metadata["date"],
        "description": metadata["description"],
        "content": content,
        "content_markdown": content,
    }


def _extract_product(soup: BeautifulSoup) -> dict:
    """Extract e-commerce product information."""
    title = soup.find("h1") or soup.select_one('[class*="title"]')
    price = soup.select_one('[class*="price"]:not([class*="old"]):not([class*="was"])')
    description = soup.select_one('[class*="description"]')
    images = [img.get("src", "") for img in soup.select('[class*="image"] img, [class*="gallery"] img')[:5]]

    return {
        "title": title.get_text(strip=True) if title else "",
        "price": price.get_text(strip=True) if price else "",
        "description": description.get_text(strip=True)[:1000] if description else "",
        "images": images,
    }


def _extract_tables(soup: BeautifulSoup) -> dict:
    """Extract all tables from page."""
    tables = []
    for i, table in enumerate(soup.find_all("table")[:5]):  # Limit to 5 tables
        rows = table.find_all("tr")
        if rows:
            headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
            data_rows = []
            for row in rows[1:11]:  # Limit to 10 rows per table
                cells = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
                if headers and len(cells) == len(headers):
                    data_rows.append(dict(zip(headers, cells)))
                elif cells:
                    data_rows.append({"data": cells})
            tables.append({"headers": headers, "rows": data_rows})

    return {"tables": tables}


def _extract_links(soup: BeautifulSoup) -> dict:
    """Extract links grouped by domain."""
    links = {}
    for a in soup.find_all("a", href=True)[:50]:
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if href.startswith("http") and text:
            # Extract domain
            domain_match = re.match(r"https?://([^/]+)", href)
            if domain_match:
                domain = domain_match.group(1)
                if domain not in links:
                    links[domain] = []
                links[domain].append({"text": text[:100], "href": href})

    return {"links_by_domain": links}


def _extract_with_schema(soup: BeautifulSoup, schema: dict) -> dict:
    """Extract data using custom schema."""
    result = {}
    for field, selector in schema.items():
        elem = soup.select_one(selector)
        result[field] = elem.get_text(strip=True) if elem else ""
    return result
