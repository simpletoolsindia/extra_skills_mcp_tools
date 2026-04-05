"""Tool schemas matching the MCP spec."""

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": "Search the web via a local SearXNG instance. Returns structured results without requiring API keys.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5, max: 20)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_web_content",
        "description": "Fetch a webpage and extract clean, LLM-friendly content. Removes navigation, ads, and other noise.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch",
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum characters to return (default: 8000). Content is chunked if needed.",
                    "default": 8000,
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "scrape_dynamic",
        "description": "Scrape JavaScript-heavy pages using Playwright headless browser. Use for SPAs, infinite scroll, or sites requiring JS execution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape",
                },
                "selector": {
                    "type": "string",
                    "description": "Optional CSS selector to extract specific content only",
                },
                "wait_for": {
                    "type": "string",
                    "description": "Optional CSS selector to wait for before extracting",
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum characters to return (default: 15000)",
                    "default": 15000,
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "extract_structured",
        "description": "Extract structured data (articles, products, tables) using scrapling's fast CSS-based extraction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "html_content": {
                    "type": "string",
                    "description": "Raw HTML content to parse",
                },
                "extraction_type": {
                    "type": "string",
                    "enum": ["article", "ecommerce", "table", "links"],
                    "description": "Type of structured data to extract",
                    "default": "article",
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector to target specific element",
                },
                "custom_selector": {
                    "type": "string",
                    "description": "Custom CSS selector for links extraction",
                },
            },
            "required": ["html_content", "extraction_type"],
        },
    },
    {
        "name": "scrape_freedium",
        "description": "Scrape Medium articles via Freedium (free alternative to Medium paywall). Extracts title, author, publication, date, content, and tags.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Freedium URL or article path (e.g., https://freedium-mirror.cfd/ARTICLE_ID or /ARTICLE_ID)",
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum characters of content to return (default: 20000)",
                    "default": 20000,
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "list_freedium_articles",
        "description": "List articles available on Freedium homepage or category pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Freedium URL (default: homepage)",
                    "default": "https://freedium-mirror.cfd/",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of articles to return (default: 20)",
                    "default": 20,
                },
            },
        },
    },
    {
        "name": "run_code",
        "description": "Run LLM-generated code in a sandboxed environment. Supports Python, JavaScript, and Bash. Has security checks and timeout limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to execute",
                },
                "language": {
                    "type": "string",
                    "description": "Programming language (python, javascript, bash)",
                    "default": "python",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds (default: 30, max: 60)",
                    "default": 30,
                },
                "args": {
                    "type": "array",
                    "description": "Command-line arguments to pass to the script",
                    "items": {"type": "string"},
                },
            },
            "required": ["code", "language"],
        },
    },
    {
        "name": "run_python_snippet",
        "description": "Run Python code with optional common imports pre-loaded (json, math, re, datetime, collections, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to run",
                },
                "imports": {
                    "type": "array",
                    "description": "Common modules to import (json, math, re, datetime, collections, itertools, functools)",
                    "items": {"type": "string"},
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum execution time (default: 30)",
                    "default": 30,
                },
            },
            "required": ["code"],
        },
    },
    {
        "name": "test_code_snippet",
        "description": "Run code and verify it produces expected output. Useful for validating LLM-generated solutions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to run",
                },
                "language": {
                    "type": "string",
                    "description": "Language (default: python)",
                    "default": "python",
                },
                "expected_output": {
                    "type": "string",
                    "description": "Expected stdout output to validate against",
                },
            },
            "required": ["code"],
        },
    },
    {
        "name": "run_command",
        "description": "Execute a whitelisted system command in a sandboxed environment. Only safe, read-only and file-operation commands are allowed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute (from the allowed set: ls, cp, mv, rm, cat)",
                },
                "args": {
                    "type": "array",
                    "description": "Arguments for the command",
                    "items": {"type": "string"},
                    "default": [],
                },
            },
            "required": ["command"],
        },
    },
]
