# MCP Unified Server — 86 Tools for Agentic AI

> **100% Self-Hosted** | **Docker Compose** | **Remote Access Ready**

---

## Quick Start

```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start.sh
```

**That's it!** Everything runs in Docker containers.

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| **MCP Server** | 7710 | TCP - Remote access |
| **SearXNG** | 7711 | Web search |
| **LiteLLM** | 7713 | Local LLM gateway |
| **PostgreSQL** | 7714 | Database |
| **Redis** | 7715 | Cache |

---

## Remote Access

### Option 1: SSH Tunnel (Recommended)

```bash
# From your local machine, tunnel to remote server
ssh -L 7710:localhost:7710 user@your-server.com

# Then use MCP normally
```

### Option 2: Direct Connection

```bash
# Connect to remote MCP server
nc your-server.com 7710

# Send JSON-RPC requests
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
```

### Option 3: Claude Code (Remote)

Add to your local `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "remote-mcp": {
      "command": "ssh",
      "args": ["-L", "7710:localhost:7710", "user@your-server.com", "nc", "localhost", "7710"]
    }
  }
}
```

### Option 4: Docker Exec (Same Machine)

```bash
# Run commands inside container
docker exec mcp-server python -m mcp_server

# Or attach to running container
docker attach mcp-server
```

---

## All 86 Tools

### 🌐 Web Search (4)
`searxng_search`, `search_images`, `search_news`, `searxng_health`

### 📖 Web Scraping (10)
`fetch_web_content`, `scrape_dynamic`, `extract_structured`, `scrape_freedium`, `firecrawl_scrape`, `firecrawl_crawl`, `webclaw_crawl`, `webclaw_extract_article`, `browserbase_browse`, `list_freedium_articles`

### 📰 News & Research (14)
- **Hacker News:** `hackernews_top`, `hackernews_new`, `hackernews_best`, `hackernews_ask`, `hackernews_show`, `hackernews_get_comments`, `hackernews_user`
- **Wikipedia:** `wikipedia_search`, `wikipedia_get_article`, `wikipedia_related`
- **HuggingFace:** `huggingface_search_models`, `huggingface_search_datasets`, `huggingface_model_info`, `huggingface_trending`

### 🐙 GitHub (6)
`github_repo`, `github_readme`, `github_issues`, `github_commits`, `github_search_repos`, `github_file_content`

### 💻 Code Execution (4)
`run_code`, `run_python_snippet`, `test_code_snippet`, `run_command`

### 📊 Data & Charts (11)
- **Pandas:** `pandas_create`, `pandas_filter`, `pandas_aggregate`, `pandas_correlation`, `pandas_outliers`
- **Charts:** `plot_line`, `plot_bar`, `plot_pie`, `plot_scatter`, `plot_histogram`, `generate_chart_spec`

### 📺 YouTube (6)
`youtube_transcript`, `youtube_transcript_timed`, `youtube_search`, `youtube_video_info`, `youtube_batch_transcribe`, `youtube_summarize`

### 🧠 Engineering Intelligence (17)
- **Analysis:** `engi_task_classify`, `engi_repo_scope_find`, `engi_flow_summarize`, `engi_bug_trace`
- **Planning:** `engi_implementation_plan`, `engi_poc_plan`, `engi_impact_analyze`, `engi_test_select`
- **Docs:** `engi_doc_context_build`, `engi_doc_update_plan`
- **Memory:** `engi_memory_checkpoint`, `engi_memory_restore`
- **Thinking:** `thinking_session_create`, `thinking_step`, `thinking_revoke`, `thinking_summary`, `analyze_problem`

### 💾 Files (9)
- **Operations:** `file_read`, `file_write`, `file_list`, `file_info`, `file_search`
- **Conversion:** `markitdown_html_to_md`, `markitdown_url_to_md`, `markitdown_file_to_md`, `markitdown_md_to_html`

### 🔧 Research (5)
`research_start`, `research_add_source`, `research_complete`, `research_report`, `searxng_health`

---

## Docker Commands

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all containers |
| `docker-compose down` | Stop all containers |
| `docker-compose logs -f` | View logs |
| `docker-compose logs -f mcp-server` | View MCP logs |
| `docker-compose restart` | Restart all |
| `docker-compose ps` | Check status |

---

## Pi5 / Dokploy Deployment

```bash
# Clone and deploy
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start.sh

# Access remotely
ssh -L 7710:localhost:7710 pi@your-pi.local
```

---

## Examples

### Search the Web
```
searxng_search("latest AI news 2024")
```

### Get YouTube Transcript
```
youtube_transcript("https://youtube.com/watch?v=XYZ123")
```

### Bug Analysis
```
engi_task_classify("Fix login crash", ["auth"])
engi_bug_trace(["src/auth.py"], "crashes empty password")
```

---

## License

MIT - Free for personal and commercial use.

⭐ **Star on GitHub!**
