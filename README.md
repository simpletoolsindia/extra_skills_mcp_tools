# MCP Server Suite — 83 Tools for Claude Code

> Self-hosted MCP server with **83 tools** for AI workflows. No API keys required.

---

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# 2. Run installation script
./install-claude-code.sh

# 3. Restart Claude Code
claude
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MCP Servers (via ~/.claude/settings.json)            │    │
│  │                                                       │    │
│  │  • mcp-server        → 83 Tools (Web, GitHub, etc.) │    │
│  │  • knowledge-graph   → SQLite Memory                │    │
│  │  • sequential-thinking → Step-by-step Reasoning    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker Services                           │
│                                                             │
│  MCP Server  → :7710    │  ChromaDB  → :8000               │
│  Firecrawl   → :7172    │  PostgreSQL → :7173               │
│  Redis       → :7174    │  SearXNG   → Pi5 :7171           │
└─────────────────────────────────────────────────────────────┘
```

---

## MCP Servers

### 1. MCP Server (83 Tools) ✅

**Docker Container**: `mcp-server` (port 7710)

| Category | Tools | Description |
|----------|-------|-------------|
| 🌐 Web Search | 4 | SearXNG search, images, news |
| 📖 Web Scraping | 7 | fetch, scrape, extract |
| 📰 News | 7 | Hacker News, search |
| 🐙 GitHub | 6 | repos, commits, issues |
| 📺 YouTube | 6 | transcript, search, summarize |
| 💻 Code | 4 | Python sandbox, test |
| 📊 Data | 11 | Pandas, charts |
| 🧠 Intelligence | 17 | task classify, bug trace, memory |
| 💾 Files | 5 | read, write, list |

### 2. Knowledge Graph 🆕

**NPX**: `npx -y knowledgegraph-mcp`

Persistent memory across conversations using SQLite.

```
Claude: Remember that I prefer dark mode
Claude: What mode did I say I prefer?
Claude: You said you prefer dark mode.
```

### 3. Sequential Thinking 🆕

**NPX**: `npx -y @modelcontextprotocol/server-sequential-thinking`

Step-by-step problem solving with dynamic revision.

```
Task: Build a React app from scratch
Thought: I need to set up the project first
Next Thought: I'll use create-react-app as a base
... (continues with structured reasoning)
```

---

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| MCP Server | 7710 | Main MCP protocol server |
| SearXNG | 7171 | Self-hosted web search (Pi5) |
| Firecrawl | 7172 | Advanced web scraping |
| PostgreSQL | 7173 | Database |
| Redis | 7174 | Cache |
| ChromaDB | 8000 | Vector database for RAG |

---

## Installation

### Prerequisites

- Docker & Docker Compose
- Node.js (optional, for NPX MCPs)
- Pi5 IP (for remote SearXNG)

### Steps

```bash
# 1. Clone
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# 2. Run installer
./install-claude-code.sh

# 3. Enter Pi5 IP when prompted (default: 192.168.0.2)

# 4. Restart Claude Code
claude
```

### Manual Setup

If you prefer manual setup:

```bash
# Start Docker services
docker compose -f docker-compose.local.yml up -d

# Configure Claude Code
cat >> ~/.claude/settings.json << 'EOF'
{
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-c", "from mcp_server.server import run; run()"]
    },
    "knowledge-graph": {
      "command": "npx",
      "args": ["-y", "knowledgegraph-mcp"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
EOF
```

---

## Pi5 (Remote) Setup

SearXNG runs on Pi5 for always-on search:

```bash
# On Pi5
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start-remote.sh
```

Then enter Pi5 IP during installation.

---

## Commands

```bash
# Start all services
docker compose -f docker-compose.local.yml up -d

# Stop all services
docker compose -f docker-compose.local.yml down

# View logs
docker compose -f docker-compose.local.yml logs -f mcp-server

# Rebuild after changes
docker compose -f docker-compose.local.yml up -d --build
```

---

## Testing Tools

```bash
# Test SearXNG
docker exec mcp-server python -c "
from mcp_server.tools.web_search import web_search
print(web_search('hello', limit=3))
"

# Test GitHub
docker exec mcp-server python -c "
from mcp_server.tools.github import search_repositories
print(search_repositories(query='python', limit=3))
"

# Test YouTube
docker exec mcp-server python -c "
from mcp_server.tools.youtube_transcript import get_transcript_from_url
print(get_transcript_from_url(url='https://youtube.com/watch?v=dQw4w9WgXcQ'))
"
```

---

## All 83 Tools

### 🌐 Web Search (4)
- `searxng_search` - Search the web
- `search_images` - Image search
- `search_news` - News search
- `searxng_health` - Check SearXNG status

### 📖 Web Scraping (7)
- `fetch_web_content` - Fetch URL content
- `scrape_dynamic` - JavaScript pages
- `extract_structured` - Structured extraction
- `scrape_freedium` - Medium articles
- `firecrawl_scrape` - Advanced scraping
- `webclaw_crawl` - Web crawling
- `browserbase_browse` - Browser automation

### 📰 News (7)
- `hackernews_top` - Top stories
- `hackernews_new` - New stories
- `hackernews_best` - Best stories
- `hackernews_ask` - Ask HN
- `hackernews_show` - Show HN
- `hackernews_get_comments` - Get comments
- `hackernews_user` - User info

### 🐙 GitHub (6)
- `github_repo` - Get repo info
- `github_readme` - Get README
- `github_issues` - List issues
- `github_commits` - List commits
- `github_search_repos` - Search repos
- `github_file_content` - Get file content

### 📺 YouTube (6)
- `youtube_transcript` - Get transcript
- `youtube_transcript_timed` - Timed transcript
- `youtube_search` - Search videos
- `youtube_video_info` - Video info
- `youtube_batch_transcribe` - Batch transcription
- `youtube_summarize` - Summarize video

### 💻 Code Execution (4)
- `run_code` - Run code (allowlist)
- `run_python_snippet` - Run Python
- `test_code_snippet` - Test code

### 📊 Data & Charts (11)
- `pandas_create` - Create DataFrame
- `pandas_filter` - Filter data
- `pandas_aggregate` - Aggregate
- `pandas_correlation` - Correlation
- `pandas_outliers` - Detect outliers
- `plot_line` - Line chart
- `plot_bar` - Bar chart
- `plot_pie` - Pie chart
- `plot_scatter` - Scatter plot
- `plot_histogram` - Histogram
- `generate_chart_spec` - Chart spec

### 🧠 Intelligence (17)
- `engi_task_classify` - Classify task
- `engi_repo_scope_find` - Find scope
- `engi_flow_summarize` - Summarize flow
- `engi_bug_trace` - Trace bug
- `engi_implementation_plan` - Plan implementation
- `engi_poc_plan` - POC plan
- `engi_impact_analyze` - Impact analysis
- `engi_test_select` - Select tests
- `engi_doc_context_build` - Build docs
- `engi_doc_update_plan` - Plan docs
- `engi_memory_checkpoint` - Save memory
- `engi_memory_restore` - Restore memory
- `thinking_session_create` - Create session
- `thinking_step` - Think step
- `thinking_revoke` - Revise
- `thinking_summary` - Get summary
- `analyze_problem` - Analyze

### 💾 Files (5)
- `file_read` - Read file
- `file_write` - Write file
- `file_list` - List directory
- `file_info` - File info
- `file_search` - Search files

### 📚 HuggingFace (4)
- `huggingface_search_models` - Search models
- `huggingface_search_datasets` - Search datasets
- `huggingface_model_info` - Model info
- `huggingface_trending` - Trending

### 📝 Markitdown (4)
- `markitdown_html_to_md` - HTML to Markdown
- `markitdown_url_to_md` - URL to Markdown
- `markitdown_file_to_md` - File to Markdown
- `markitdown_md_to_html` - Markdown to HTML

---

## Troubleshooting

### SearXNG returns 403
- Ensure Pi5 SearXNG has `limiter: false` in settings.yml
- Restart SearXNG: `ssh pi5 "docker restart searxng"`

### SSL Certificate Error
- Already fixed with ca-certificates in Dockerfile
- Rebuild: `docker compose up -d --build mcp-server`

### ChromaDB Connection Error
- Check ChromaDB is running: `docker ps | grep chromadb`
- Restart: `docker compose restart chromadb`

### Wikipedia Not Working
- Wikipedia removed due to rate limiting
- Use SearXNG for Wikipedia content instead

---

## License

MIT
