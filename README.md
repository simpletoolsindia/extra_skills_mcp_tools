# MCP Server — Local LLM Tool Ecosystem

API-free MCP server enabling local LLMs (Qwen, Gemma, DeepSeek, GLM) to:
- Perform web search via **SearXNG**
- Fetch and transform web content
- Execute controlled system commands

## Prerequisites

### SearXNG (required for web search)

**Start via Docker:**

```bash
docker run -d \
  -p 8888:8080 \
  -v "$(pwd)/searxng-data:/etc/searxng" \
  --name searxng \
  searxng/searxng
```

**Configure SearXNG** by creating `searxng-data/settings.yml`:

```yaml
use_default_settings: true

general:
  instance_name: "MCP Server Search"

search:
  safe_search: 0
  formats:
    - html
    - json

server:
  secret_key: "your-secret-key-here"
  limiter: false
```

Also create `searxng-data/limiter.toml`:

```toml
[botdetection]
trusted_proxies = ['127.0.0.0/8', '::1']

[botdetection.ip_limit]
filter_link_local = false
link_token = false

[botdetection.ip_lists]
pass_ip = ['127.0.0.0/8', '::1']
```

**Restart after config:**
```bash
docker stop searxng && docker rm searxng
docker run -d -p 8888:8080 \
  -v "$(pwd)/searxng-data:/etc/searxng" \
  --name searxng searxng/searxng
```

### Python Dependencies

```bash
uv venv .venv && source .venv/bin/activate
uv pip install -e .
```

## Usage

```bash
SEARXNG_BASE_URL=http://localhost:8888 python -m mcp_server
```

Or with the installed CLI:

```bash
SEARXNG_BASE_URL=http://localhost:8888 mcp-server
```

## Tools

| Tool | Description |
|------|-------------|
| `web_search` | Search the web via local SearXNG |
| `fetch_web_content` | Extract clean content from a URL (readability-lxml) |
| `scrape_dynamic` | Scrape JavaScript-heavy pages using Playwright headless browser |
| `extract_structured` | Extract structured data (articles, products, tables) using CSS selectors |
| `scrape_freedium` | Scrape Medium articles via Freedium (bypasses paywall) |
| `list_freedium_articles` | List articles available on Freedium homepage |
| `run_code` | Run LLM-generated code in sandboxed environment |
| `run_python_snippet` | Run Python code with pre-loaded common imports |
| `test_code_snippet` | Run code and verify expected output |
| `run_command` | Execute whitelisted system commands |

### New Tools Added

#### Playwright Scraping (`scrape_dynamic`)
For pages that require JavaScript execution (SPAs, infinite scroll, etc.):
```python
{
    "url": "https://example.com",  # required
    "selector": ".main-content",   # optional CSS selector
    "wait_for": ".loaded",         # optional - wait for element
    "max_length": 15000            # max characters
}
```
Requires: `pip install playwright && playwright install chromium`

#### Scrapling Extraction (`extract_structured`)
Fast CSS-based extraction for structured data:
```python
{
    "html_content": "...",         # raw HTML
    "extraction_type": "article",  # article|ecommerce|table|links
    "selector": ".content",        # optional CSS selector
    "custom_selector": "a"         # for links pattern
}
```
Requires: `pip install scrapling`

**Environment variables:**
- `PLAYWRIGHT_HEADLESS=true` (default) - Run browser in headless mode
- `BROWSER_TIMEOUT=15` - Page load timeout in seconds

#### Freedium Scraping (`scrape_freedium`, `list_freedium_articles`)
Access Medium articles without paywall:
```python
{
    "url": "https://freedium-mirror.cfd/ARTICLE_ID",  # or just "/ARTICLE_ID"
    "max_length": 20000  # optional
}
```
Returns: title, author, publication, date, content, tags

#### Code Sandbox (`run_code`, `run_python_snippet`, `test_code_snippet`)
Run LLM-generated code safely:
```python
{
    "code": "print('Hello, World!')",
    "language": "python",  # python, javascript, bash
    "timeout": 30,
    "args": []  # optional command-line args
}
```
- Security: Blocks dangerous patterns (os.system, eval, etc.)
- Timeout: Max 60 seconds (configurable via SANDBOX_TIMEOUT env)
- Languages: Python, JavaScript (Node.js), Bash

## Security

- `run_command` uses strict allowlist — only `ls`, `cp`, `mv`, `rm`, `cat` by default
- Read-only commands (`ls`, `cat`) can use absolute paths
- Write commands (`rm`, `cp`, `mv`) are restricted to relative paths
- `rm` blocks dangerous flags (`-rf`, `-r`) and critical paths (`/`, `/tmp`, `/etc`)
- All commands: no shell metacharacters, no env vars, no path traversal
- Subprocess isolation with 10s timeout, no shell=True

## Testing

```bash
# All tests (requires network)
python -m pytest tests/ -v

# Offline verification only
SKIP_NETWORK=1 python tests/verify.py

# Live verification
python tests/verify.py
```

## Claude Code Integration

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/Users/sridhar/.local/bin/python3.12",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:8888",
        "PYTHONPATH": "/Users/sridhar/code/mcp-server/src"
      }
    }
  }
}
```

Restart Claude Code to pick up the tools.
