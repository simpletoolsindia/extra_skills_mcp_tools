# MCP Unified Server — 86 Tools for Agentic AI

> **100% Self-Hosted** | No API Keys Required | Privacy-First

[![GitHub Stars](https://img.shields.io/github/stars/simpletoolsindia/extra_skills_mcp_tools?style=social)](https://github.com/simpletoolsindia/extra_skills_mcp_tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tools: 86](https://img.shields.io/badge/Tools-86-success?style=flat)](#all-86-tools)

---

## What is This?

An **MCP (Model Context Protocol) server** that gives AI assistants superpowers:

| Category | Tools | What It Does |
|----------|-------|--------------|
| 🌐 **Web Search** | 4 | Privacy-respecting search (SearXNG) |
| 📖 **Web Scraping** | 10 | Extract content from any website |
| 📰 **News** | 14 | Hacker News, Wikipedia, HuggingFace |
| 🐙 **GitHub** | 6 | Explore repos, issues, code |
| 💻 **Code** | 4 | Execute Python, JS, Bash safely |
| 📊 **Data** | 11 | Pandas, Matplotlib, charts |
| 📺 **YouTube** | 6 | Transcripts, search, summaries |
| 🧠 **Intelligence** | 17 | Bug tracing, planning, analysis |
| 💾 **Files** | 9 | Read/write files, convert docs |
| 🔧 **System** | 5 | Commands, research sessions |

---

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repo
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# Install (creates virtual environment)
pip install -e .

# Install Playwright browser (for JS-heavy pages)
playwright install chromium
```

### 2. Start Docker Services (Optional but Recommended)

```bash
# Start SearXNG web search on port 7711
docker run -d -p 7711:8080 --name searxng searxng/searxng
```

### 3. Run MCP Server

```bash
# Set environment
export SEARXNG_BASE_URL=http://localhost:7711

# Start server
python -m mcp_server
```

### 4. Configure Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:7711"
      }
    }
  }
}
```

**Find your Python path:** `which python3` (Mac/Linux) or `where python` (Windows)

---

## Port Configuration

Docker services use ports **7711 onwards**:

| Port | Service | Resources | Purpose |
|------|---------|-----------|---------|
| 7711 | SearXNG | Lightweight | Web search engine |
| 7712 | Firecrawl | ⚠️ 6 CPU + 12GB | Advanced scraping (optional) |
| 7713 | LiteLLM | Lightweight | Local LLM gateway |
| 7714 | PostgreSQL | Lightweight | Database |
| 7715 | Redis | Lightweight | Cache |

### Firecrawl (Optional)

**Requires:** 6 CPU cores + 12GB RAM

Not needed for Pi5 or lightweight servers. Use built-in scrapers instead:

- **Playwright** — JS-heavy pages (already installed)
- **Scrapling** — Fast CSS extraction (built-in)
- **Webclaw** — Article extraction (built-in)

---

## All 86 Tools

### 🌐 Web Search (4)

| Tool | Description |
|------|-------------|
| `searxng_search` | Search the web (privacy-respecting) |
| `search_images` | Find images |
| `search_news` | Get news articles |
| `searxng_health` | Check if search is working |

### 📖 Web Scraping (10)

| Tool | Description |
|------|-------------|
| `fetch_web_content` | Get clean text from URL |
| `scrape_dynamic` | JavaScript-heavy pages (Playwright) |
| `extract_structured` | Extract articles/products (Scrapling) |
| `scrape_freedium` | Read Medium articles free |
| `firecrawl_scrape` | Advanced scraping (Firecrawl - optional) |
| `firecrawl_crawl` | Multi-page crawling |
| `webclaw_crawl` | Custom CSS selector extraction |
| `webclaw_extract_article` | Extract article content |
| `browserbase_browse` | Browser automation fallback |

### 📰 News & Research (14)

**Hacker News (7):**
| Tool | Description |
|------|-------------|
| `hackernews_top` | Top stories |
| `hackernews_new` | Newest stories |
| `hackernews_best` | Best stories |
| `hackernews_ask` | Ask HN posts |
| `hackernews_show` | Show HN posts |
| `hackernews_get_comments` | Story comments |
| `hackernews_user` | User profile |

**Wikipedia (3):**
| Tool | Description |
|------|-------------|
| `wikipedia_search` | Search Wikipedia |
| `wikipedia_get_article` | Get article content |
| `wikipedia_related` | Related articles |

**HuggingFace (4):**
| Tool | Description |
|------|-------------|
| `huggingface_search_models` | Find AI models |
| `huggingface_search_datasets` | Find datasets |
| `huggingface_model_info` | Model details |
| `huggingface_trending` | Trending models |

### 🐙 GitHub (6)

| Tool | Description |
|------|-------------|
| `github_repo` | Repository info |
| `github_readme` | Get README |
| `github_issues` | List issues |
| `github_commits` | Recent commits |
| `github_search_repos` | Search repositories |
| `github_file_content` | Get file contents |

### 💻 Code Execution (4)

| Tool | Description |
|------|-------------|
| `run_code` | Execute code safely |
| `run_python_snippet` | Python with imports |
| `test_code_snippet` | Run & verify output |
| `run_command` | Run shell commands |

**Supported:** Python, JavaScript (Node.js), Bash

### 📊 Data & Charts (11)

**Pandas (5):**
| Tool | Description |
|------|-------------|
| `pandas_create` | Create DataFrame |
| `pandas_filter` | Filter data |
| `pandas_aggregate` | Group & aggregate |
| `pandas_correlation` | Compute correlations |
| `pandas_outliers` | Detect outliers |

**Charts (6):**
| Tool | Description |
|------|-------------|
| `plot_line` | Line charts |
| `plot_bar` | Bar charts |
| `plot_pie` | Pie charts |
| `plot_scatter` | Scatter plots |
| `plot_histogram` | Histograms |
| `generate_chart_spec` | Ant Design specs |

### 📺 YouTube (6)

| Tool | Description |
|------|-------------|
| `youtube_transcript` | Get transcript |
| `youtube_transcript_timed` | Transcript with timestamps |
| `youtube_search` | Search videos |
| `youtube_video_info` | Video metadata |
| `youtube_batch_transcribe` | Multiple videos |
| `youtube_summarize` | Create summary |

### 🧠 Engineering Intelligence (17)

> **97% token reduction** for large codebases

**Analysis (4):**
| Tool | Description |
|------|-------------|
| `engi_task_classify` | Classify task type |
| `engi_repo_scope_find` | Find relevant files |
| `engi_flow_summarize` | Compact flow description |
| `engi_bug_trace` | Pinpoint bug causes |

**Planning (4):**
| Tool | Description |
|------|-------------|
| `engi_implementation_plan` | Step-by-step plan |
| `engi_poc_plan` | POC scaffold |
| `engi_impact_analyze` | Estimate blast radius |
| `engi_test_select` | Minimum test set |

**Documentation (2):**
| Tool | Description |
|------|-------------|
| `engi_doc_context_build` | Build doc context |
| `engi_doc_update_plan` | Find docs to update |

**Memory (2):**
| Tool | Description |
|------|-------------|
| `engi_memory_checkpoint` | Save task state |
| `engi_memory_restore` | Restore checkpoint |

**Sequential Thinking (5):**
| Tool | Description |
|------|-------------|
| `thinking_session_create` | Start session |
| `thinking_step` | Add thought |
| `thinking_revoke` | Revise thought |
| `thinking_summary` | Get summary |
| `analyze_problem` | Structured analysis |

### 💾 File System (9)

**File Operations (5):**
| Tool | Description |
|------|-------------|
| `file_read` | Read file |
| `file_write` | Write file |
| `file_list` | List directory |
| `file_info` | File details |
| `file_search` | Search files |

**Document Conversion (4):**
| Tool | Description |
|------|-------------|
| `markitdown_html_to_md` | HTML → Markdown |
| `markitdown_url_to_md` | URL → Markdown |
| `markitdown_file_to_md` | File → Markdown |
| `markitdown_md_to_html` | Markdown → HTML |

### 🔧 System (5)

**Research (4):**
| Tool | Description |
|------|-------------|
| `research_start` | Start research |
| `research_add_source` | Add source |
| `research_complete` | Complete research |
| `research_report` | Get report |

**System (1):**
| Tool | Description |
|------|-------------|
| `searxng_health` | Health check |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_BASE_URL` | http://localhost:7711 | SearXNG search URL |
| `FIRECRAWL_HOST` | http://localhost:7712 | Firecrawl URL (optional) |
| `PLAYWRIGHT_HEADLESS` | true | Headless browser mode |
| `BROWSER_TIMEOUT` | 15 | Page load timeout (seconds) |
| `GITHUB_TOKEN` | - | GitHub API token (optional) |
| `HF_TOKEN` | - | HuggingFace token (optional) |

---

## Docker Deployment

### Pi5 / Dokploy

```bash
# 1. Clone
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# 2. SSL Certificates
sudo certbot certonly --standalone -d search.sridharhomelab.in

# 3. Copy certificates
sudo cp /etc/letsencrypt/live/search.sridharhomelab.in/fullchain.pem docker/nginx/certs/cert.pem
sudo cp /etc/letsencrypt/live/search.sridharhomelab.in/privkey.pem docker/nginx/certs/key.pem

# 4. Deploy all services
cd docker
docker-compose up -d
```

### Access URLs

| Service | URL |
|---------|-----|
| Search | https://search.sridharhomelab.in |
| API Gateway | https://api.sridharhomelab.in |

---

## Troubleshooting

### "SearXNG not found"
```bash
# Start SearXNG on port 7711
docker run -d -p 7711:8080 --name searxng searxng/searxng

# Verify
curl "http://localhost:7711/search?q=test&format=json"
```

### "Module not found"
```bash
pip install -e .
```

### Playwright errors
```bash
playwright install chromium
```

### Permission denied
```bash
chmod +x install.sh
```

---

## Example Usage

### Research: "Latest AI developments"
```
1. searxng_search("AI agents 2024 developments")
2. wikipedia_search("Artificial Intelligence")
3. hackernews_top(limit=10)
4. huggingface_trending()
```

### Bug Fix: "Login crash"
```
1. engi_task_classify("Fix login crash when password empty", ["auth"])
2. engi_repo_scope_find("/project", "login bug", "bug")
3. engi_bug_trace(["src/auth.py"], "crashes when password empty")
4. engi_implementation_plan("Fix password validation", scope=["src/auth.py"])
```

### YouTube: "Get video transcript"
```
1. youtube_transcript("https://youtube.com/watch?v=XYZ123")
2. youtube_summarize(transcript, max_words=500)
```

---

## License

MIT — Free for personal and commercial use.

## Credits

Built for the AI agent community.

Tools: SearXNG, Playwright, Scrapling, Pandas, Matplotlib, Invidious, engi-mcp

---

⭐ **Star on GitHub if this helped you!**
