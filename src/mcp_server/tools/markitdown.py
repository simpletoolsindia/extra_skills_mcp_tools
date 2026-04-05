"""Markitdown MCP - Convert various document formats to Markdown."""

from __future__ import annotations

import os
import re
from typing import Optional, Dict, Any

try:
    import httpx
    HTTpx_AVAILABLE = True
except ImportError:
    HTTpx_AVAILABLE = False


def clean_markdown(text: str) -> str:
    """Clean and normalize markdown text."""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove trailing whitespace
    text = '\n'.join(line.rstrip() for line in text.splitlines())
    return text.strip()


def html_to_markdown(html: str) -> dict:
    """
    Convert HTML to Markdown.

    Args:
        html: HTML content

    Returns:
        dict with keys: markdown, error
    """
    if not HTTpx_AVAILABLE:
        return {"markdown": "", "error": "httpx not installed"}

    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        def element_to_md(element):
            if not element:
                return ""

            md = ""

            # Handle headings
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                text = element.get_text(strip=True)
                md = f"{'#' * level} {text}\n\n"

            # Handle paragraphs
            elif element.name == 'p':
                md = element.get_text(strip=True) + "\n\n"

            # Handle lists
            elif element.name == 'ul':
                for li in element.find_all('li', recursive=False):
                    md += f"- {li.get_text(strip=True)}\n"
                md += "\n"

            elif element.name == 'ol':
                for i, li in enumerate(element.find_all('li', recursive=False), 1):
                    md += f"{i}. {li.get_text(strip=True)}\n"
                md += "\n"

            # Handle code blocks
            elif element.name in ['pre', 'code']:
                code = element.get_text()
                lang = element.get('class', [''])[0].replace('language-', '') if element.name == 'code' else ''
                md = f"```{lang}\n{code}\n```\n\n"

            # Handle blockquotes
            elif element.name == 'blockquote':
                text = element.get_text(strip=True)
                md = f"> {text}\n\n"

            # Handle horizontal rules
            elif element.name == 'hr':
                md = "---\n\n"

            # Handle divs (just process children)
            elif element.name == 'div':
                for child in element.children:
                    if hasattr(child, 'name') and child.name:
                        md += element_to_md(child)
                    else:
                        md += str(child)

            # Handle tables
            elif element.name == 'table':
                rows = element.find_all('tr')
                if rows:
                    # Header row
                    header = rows[0].find_all(['th', 'td'])
                    md += "| " + " | ".join(th.get_text(strip=True) for th in header) + " |\n"
                    md += "| " + " | ".join("---" for _ in header) + " |\n"

                    # Body rows
                    for row in rows[1:]:
                        cells = row.find_all(['td'])
                        md += "| " + " | ".join(td.get_text(strip=True) for td in cells) + " |\n"
                    md += "\n"

            # Handle links
            elif element.name == 'a':
                href = element.get('href', '')
                text = element.get_text(strip=True)
                if href:
                    md = f"[{text}]({href})"
                else:
                    md = text

            # Handle images
            elif element.name == 'img':
                src = element.get('src', '')
                alt = element.get('alt', '')
                md = f"![{alt}]({src})"

            # Handle bold/italic
            elif element.name in ['strong', 'b']:
                text = element.get_text(strip=True)
                md = f"**{text}**"

            elif element.name in ['em', 'i']:
                text = element.get_text(strip=True)
                md = f"*{text}*"

            # Handle line breaks
            elif element.name == 'br':
                md = "\n"

            else:
                # Default: just get text
                md = element.get_text()

            return md

        # Process all top-level elements
        markdown = ""
        for element in soup.find_all(recursive=False):
            if hasattr(element, 'name') and element.name:
                markdown += element_to_md(element)

        return {"markdown": clean_markdown(markdown), "error": None}

    except ImportError:
        return {"markdown": "", "error": "beautifulsoup4 not installed"}
    except Exception as e:
        return {"markdown": "", "error": str(e)}


def url_to_markdown(url: str, max_length: int = 50000) -> dict:
    """
    Fetch URL and convert to Markdown.

    Args:
        url: URL to fetch
        max_length: Maximum markdown length

    Returns:
        dict with keys: markdown, title, url, error
    """
    if not HTTpx_AVAILABLE:
        return {"markdown": "", "title": "", "url": url, "error": "httpx not installed"}

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; MCP-Server/1.0)",
            })
            response.raise_for_status()

        # Get title
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ""

        # Convert to markdown
        result = html_to_markdown(response.text)

        markdown = result.get("markdown", "")[:max_length]

        return {
            "markdown": markdown,
            "title": title_text,
            "url": str(response.url),
            "error": None,
        }

    except Exception as e:
        return {"markdown": "", "title": "", "url": url, "error": str(e)}


def extract_text_from_file(file_path: str) -> dict:
    """
    Extract text content from various file formats.

    Args:
        file_path: Path to file

    Returns:
        dict with keys: text, format, error
    """
    import os

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in ['.txt', '.md', '.markdown']:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
            return {"text": text, "format": "text", "error": None}

        elif ext == '.json':
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"text": json.dumps(data, indent=2), "format": "json", "error": None}

        elif ext in ['.html', '.htm']:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                html = f.read()
            result = html_to_markdown(html)
            return {"text": result.get("markdown", ""), "format": "html", "error": result.get("error")}

        elif ext in ['.csv']:
            import csv
            lines = []
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                for row in reader:
                    lines.append(" | ".join(row))
            return {"text": "\n".join(lines), "format": "csv", "error": None}

        else:
            return {"text": "", "format": ext, "error": f"Unsupported format: {ext}"}

    except Exception as e:
        return {"text": "", "format": ext, "error": str(e)}


def markdown_to_html(markdown: str) -> dict:
    """
    Convert Markdown to HTML.

    Args:
        markdown: Markdown content

    Returns:
        dict with keys: html, error
    """
    try:
        from bs4 import BeautifulSoup

        html = markdown

        # Headers
        for i in range(6, 0, -1):
            pattern = r'^' + '#' * i + r'\s+(.+)$'
            html = re.sub(pattern, f'<h{i}>\\1</h{i}>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Images
        html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', html)

        # Code blocks
        html = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code class="\1">\2</code></pre>', html, flags=re.DOTALL)

        # Inline code
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # Blockquotes
        html = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # Horizontal rules
        html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)

        # Paragraphs
        paragraphs = html.split('\n\n')
        html = '\n'.join(f'<p>{p.strip()}</p>' if not p.strip().startswith('<') else p.strip() for p in paragraphs if p.strip())

        return {"html": f"<div class='markdown'>{html}</div>", "error": None}

    except Exception as e:
        return {"html": "", "error": str(e)}