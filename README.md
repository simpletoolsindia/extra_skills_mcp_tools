# MCP Unified Server — 86 Tools for Agentic AI

> **Split Architecture** | Pi5 (Always On) + Mac (On Demand) | Cloudflare Remote Access

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     YOUR MAC                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ MCP Server  │  │   Ollama    │  │  Playwright │     │
│  │   :7710     │  │   :11434    │  │             │     │
│  └──────┬──────┘  └─────────────┘  └─────────────┘     │
│         │                                                │
└─────────┼──────────────────────────────────────────────┘
          │ HTTP
          ▼
┌─────────────────────────────────────────────────────────┐
│                      PI5 (Always On)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  SearXNG    │  │ PostgreSQL  │  │    Redis    │     │
│  │   :7711     │  │   :7714     │  │   :7715     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                                                │
│  ┌─────────────┐                                        │
│  │ Cloudflare  │ ──────► Remote Access URL              │
│  │  Tunnel     │                                        │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Setup

### 1. Pi5 Setup (Always On)

```bash
# On Pi5
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# Optional: Cloudflare Tunnel
# 1. Create tunnel at dash.cloudflare.com
# 2. Copy tunnel token
# 3. echo "CLOUDFLARE_TOKEN=your_token" > .env

./start-pi5.sh
```

### 2. Mac Setup (Your Machine)

```bash
# On Mac
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# Enter Pi5 IP (check Pi5 with: ping pi5.local)
./start.sh
# Enter Pi5 IP when asked (e.g., 192.168.1.100)
```

---

## Services

### Pi5 (Always On)

| Service | Port | Local Access | Remote Access |
|---------|------|--------------|---------------|
| SearXNG | 7711 | http://pi5.local:7711 | Cloudflare URL |
| PostgreSQL | 7714 | pi5.local:7714 | Via tunnel |
| Redis | 7715 | pi5.local:7715 | Via tunnel |
| Cloudflare | - | - | *.trycloudflare.com |

### Mac (Your Machine)

| Service | Port | Description |
|---------|------|-------------|
| MCP Server | 7710 | TCP for remote access |
| Ollama | 11434 | Local LLM (already running) |

---

## Remote Access

### Option 1: SSH Tunnel (Recommended)

```bash
# Tunnel MCP port to your Mac
ssh -L 7710:localhost:7710 pi@pi5.local

# Then access MCP normally on Mac
```

### Option 2: Cloudflare Tunnel

Access SearXNG remotely via Cloudflare:

```bash
# Configure tunnel at dash.cloudflare.com
# Point to: http://pi5.local:7711
# Access at: https://mcp-search.trycloudflare.com
```

### Option 3: Claude Code Remote

On your local Mac, add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-m", "mcp_server"]
    }
  }
}
```

---

## All 86 Tools

### 🌐 Web Search (4)
`searxng_search`, `search_images`, `search_news`, `searxng_health`

### 📖 Web Scraping (10)
`fetch_web_content`, `scrape_dynamic`, `extract_structured`, `scrape_freedium`, `firecrawl_scrape`, `firecrawl_crawl`, `webclaw_crawl`, `webclaw_extract_article`, `browserbase_browse`, `list_freedium_articles`

### 📰 News & Research (14)
- **Hacker News:** 7 tools
- **Wikipedia:** 3 tools
- **HuggingFace:** 4 tools

### 🐙 GitHub (6)
`github_repo`, `github_readme`, `github_issues`, `github_commits`, `github_search_repos`, `github_file_content`

### 💻 Code Execution (4)
`run_code`, `run_python_snippet`, `test_code_snippet`, `run_command`

### 📊 Data & Charts (11)
- **Pandas:** 5 tools
- **Charts:** 6 tools

### 📺 YouTube (6)
`youtube_transcript`, `youtube_transcript_timed`, `youtube_search`, `youtube_video_info`, `youtube_batch_transcribe`, `youtube_summarize`

### 🧠 Engineering Intelligence (17)
`engi_task_classify`, `engi_repo_scope_find`, `engi_flow_summarize`, `engi_bug_trace`, `engi_implementation_plan`, `engi_poc_plan`, `engi_impact_analyze`, `engi_test_select`, `engi_doc_context_build`, `engi_doc_update_plan`, `engi_memory_checkpoint`, `engi_memory_restore`, `thinking_session_create`, `thinking_step`, `thinking_revoke`, `thinking_summary`, `analyze_problem`

### 💾 Files (9)
- **Operations:** 5 tools
- **Conversion:** 4 tools

### 🔧 Research (5)
`research_start`, `research_add_source`, `research_complete`, `research_report`, `searxng_health`

---

## Docker Commands

### Pi5
```bash
# Start
docker-compose -f docker-compose.pi5.yml up -d

# Stop
docker-compose -f docker-compose.pi5.yml down

# Logs
docker-compose -f docker-compose.pi5.yml logs -f
```

### Mac
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f
```

---

## Environment Variables

### Pi5 (.env)
```env
CLOUDFLARE_TOKEN=your_cloudflare_tunnel_token
```

### Mac (.env)
```env
PI5_IP=192.168.1.100  # Your Pi5 IP
```

---

## Low Power Usage

**Pi5 runs only:**
- SearXNG (web search)
- PostgreSQL (database)
- Redis (cache)
- Cloudflare tunnel

**Mac runs:**
- MCP Server (when needed)
- Ollama (your LLM)
- Playwright (browser)

This means Pi5 uses minimal power (~5W) and Mac handles heavy workloads only when needed.

---

## License

MIT

⭐ **Star on GitHub!**
