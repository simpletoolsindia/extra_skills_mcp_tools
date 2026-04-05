# MCP Unified Server — 68 Tools for Agentic AI

A comprehensive Model Context Protocol server with 68+ tools for local LLM agents and AI workflows.

## Features

- **Native SearXNG** - Full-featured web search with categories, engines, time filters
- **Web Scraping** - Playwright, Scrapling, Firecrawl, Webclaw, Browserbase, Freedium
- **Search Engines** - Hacker News, Wikipedia, Hugging Face
- **GitHub** - Repos, issues, PRs, code search
- **File System** - Safe read/write with security restrictions
- **Code Execution** - Python, JavaScript, Bash sandboxed
- **Data Analysis** - Pandas operations, filtering, aggregation, correlation
- **Visualization** - Matplotlib charts, Ant Design specs
- **Document Conversion** - HTML ↔ Markdown, file extraction
- **Reasoning** - Sequential thinking, problem analysis
- **Research** - Multi-source research orchestration

## Quick Start

```bash
# Clone and install
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./install.sh

# Start server
SEARXNG_BASE_URL=http://localhost:8888 python -m mcp_server
```

## Tools by Category

### 🔍 SearXNG (4 tools)
| Tool | Description |
|------|-------------|
| `searxng_search` | Web search with categories, engines, time range |
| `search_images` | Image search |
| `search_news` | News search |
| `searxng_health` | Health check |

### 🌐 Web Scraping (10 tools)
| Tool | Description |
|------|-------------|
| `fetch_web_content` | Clean URL extraction |
| `scrape_dynamic` | JavaScript pages (Playwright) |
| `extract_structured` | CSS-based extraction |
| `scrape_freedium` | Medium articles free |
| `list_freedium_articles` | List Freedium articles |
| `firecrawl_scrape` | Firecrawl API |
| `firecrawl_crawl` | Multi-page crawl |
| `webclaw_crawl` | CSS selector crawl |
| `webclaw_extract_article` | Article extraction |
| `browserbase_browse` | Cloud browser |

### 📰 News & Articles (9 tools)
| Tool | Description |
|------|-------------|
| `hackernews_top` | Top HN stories |
| `hackernews_new` | New HN stories |
| `hackernews_best` | Best HN stories |
| `hackernews_ask` | Ask HN |
| `hackernews_show` | Show HN |
| `hackernews_get_comments` | Story comments |
| `hackernews_user` | HN user info |
| `wikipedia_search` | Wikipedia search |
| `wikipedia_get_article` | Wikipedia article |

### 🐙 GitHub (6 tools)
| Tool | Description |
|------|-------------|
| `github_repo` | Repository info |
| `github_readme` | README content |
| `github_issues` | Issue list |
| `github_commits` | Commit history |
| `github_search_repos` | Repo search |
| `github_file_content` | File content |

### 📁 File System (5 tools)
| Tool | Description |
|------|-------------|
| `file_read` | Read file |
| `file_write` | Write file |
| `file_list` | List directory |
| `file_info` | File info |
| `file_search` | Search files |

### 💻 Code Execution (3 tools)
| Tool | Description |
|------|-------------|
| `run_code` | Sandbox execution |
| `run_python_snippet` | Python with imports |
| `test_code_snippet` | Validate output |

### 📊 Data Analysis (5 tools)
| Tool | Description |
|------|-------------|
| `pandas_create` | Create DataFrame |
| `pandas_filter` | Filter data |
| `pandas_aggregate` | Aggregate |
| `pandas_correlation` | Correlation matrix |
| `pandas_outliers` | Outlier detection |

### 📈 Visualization (6 tools)
| Tool | Description |
|------|-------------|
| `plot_line` | Line chart |
| `plot_bar` | Bar chart |
| `plot_pie` | Pie chart |
| `plot_scatter` | Scatter plot |
| `plot_histogram` | Histogram |
| `generate_chart_spec` | Ant Design spec |

### 📝 Document Conversion (4 tools)
| Tool | Description |
|------|-------------|
| `markitdown_html_to_md` | HTML to Markdown |
| `markitdown_url_to_md` | URL to Markdown |
| `markitdown_file_to_md` | File to Markdown |
| `markitdown_md_to_html` | Markdown to HTML |

### 🧠 Reasoning (5 tools)
| Tool | Description |
|------|-------------|
| `thinking_session_create` | New session |
| `thinking_step` | Add step |
| `thinking_revoke` | Revise step |
| `thinking_summary` | Get summary |
| `analyze_problem` | Structured analysis |

### 🔬 Research (4 tools)
| Tool | Description |
|------|-------------|
| `research_start` | Start research |
| `research_add_source` | Add source |
| `research_complete` | Complete |
| `research_report` | Get report |

## Installation

### Prerequisites
- Python 3.11+
- Docker (for SearXNG)
- uv or pip

### 1. Start SearXNG (optional)
```bash
docker run -d -p 8888:8080 --name searxng searxng/searxng
```

### 2. Install
```bash
./install.sh
```

### 3. Configure Claude Code
Add to `~/.claude/settings.json`:
```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:8888"
      }
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_BASE_URL` | http://localhost:8888 | SearXNG instance |
| `PLAYWRIGHT_HEADLESS` | true | Headless browser |
| `BROWSER_TIMEOUT` | 15 | Page timeout (seconds) |
| `GITHUB_TOKEN` | - | GitHub API token |
| `HF_TOKEN` | - | Hugging Face token |
| `FIRECRAWL_API_TOKEN` | - | Firecrawl API key |
| `BROWSERBASE_API_KEY` | - | Browserbase key |

## License

MIT