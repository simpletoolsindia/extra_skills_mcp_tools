# MCP Server Suite — 83 Tools for Claude Code

> Self-hosted MCP server with **83 tools** for AI workflows. No API keys required.
>
> **NEW: Token Optimization** — 80%+ token reduction with 5 optimization layers

---

## Token Optimization (80%+ Savings)

This MCP server implements **comprehensive token optimization** to reduce context window usage:

| Optimization | Reduction | Description |
|--------------|-----------|-------------|
| **Tool Trimming** | 80% | 90 → 64 tools with concise descriptions |
| **Web Content** | 80-97% | Clean markdown, noise removal, token budgets |
| **Context Mode** | 98% | Store outputs externally, pass references |
| **Lazy Loading** | 91% | Load schemas on-demand |
| **Semantic Search** | 91% | 3-tool pattern for natural discovery |

### Quick Example

```bash
# Before optimization: ~13,500 tokens for tool list
# After optimization: ~2,700 tokens (80% reduction)

# Token stats
get_token_stats()  # Shows savings breakdown

# Minimal fetch (25 tokens vs ~3000)
quick_fetch(url="https://example.com", max_tokens=1500)

# Store large outputs externally (98% reduction)
ctx_store_output(tool_name="github_repo", output={...})
```

### New Optimization Tools

| Tool | Description |
|------|-------------|
| `quick_fetch` | Ultra-fast title + summary (1500 tokens max) |
| `fetch_web_content` | Clean markdown with token tracking |
| `fetch_structured` | Article/product/table extraction |
| `ctx_store_output` | Store output externally |
| `ctx_get_output` | Retrieve stored output |
| `tools_minimal` | List tools without full schemas |
| `semantic_search` | Natural language tool search |

See [`TOKEN_OPTIMIZATION.md`](TOKEN_OPTIMIZATION.md) for full documentation.

---

## Claude Code Optimization (70%+ Cost Reduction)

### Model Selection Strategy

| Model | Use Case | Cost |
|-------|----------|------|
| **Sonnet** | Most coding tasks | $3/million |
| **Opus** | Complex architecture, deep debugging | $15/million |
| **Haiku** | Code review, simple fixes | $0.25/million |

### Recommended Settings

```bash
# Add to ~/.zshrc or ~/.bashrc

# Use Sonnet as default (~60% cheaper)
claude config set --claude-code-subagent-model sonnet

# Limit thinking tokens (~70% savings)
export MAX_THINKING_TOKENS=10000

# Compact earlier (better performance)
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50
```

### Quick Commands

```bash
/cost      # Monitor token usage
/clear     # Free context reset between tasks
/compact   # Manual compaction at breakpoints
/context   # Check context usage
```

### MCP Server Best Practices

> **Warning:** Keep MCP servers under 10, total tools under 80. Excessive MCPs reduce effective context from 200k to ~70k.

See [`OPTIMIZATION_GUIDE.md`](OPTIMIZATION_GUIDE.md) for full optimization guide.

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

# Test Token Optimization
docker exec mcp-server python -c "
from src.mcp_server.server import _get_token_stats
print(_get_token_stats())
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

### ⚡ Optimization (14)
- `get_token_stats` - Token optimization statistics
- `quick_fetch` - Minimal token web fetch
- `fetch_web_content` - Optimized content extraction
- `fetch_structured` - Structured data extraction
- `fetch_with_selectors` - CSS selector extraction
- `ctx_store_output` - Store output externally
- `ctx_get_output` - Retrieve stored output
- `ctx_search` - Search stored outputs
- `ctx_session_overview` - Session summary
- `ctx_stats` - Context mode stats
- `tools_minimal` - Lazy tool list
- `tools_describe` - Load schemas on-demand
- `tools_search` - Search tools
- `semantic_search` - Natural language search

---

## Token Optimization Test Report

**Date:** 2026-04-06
**Commit:** `b2d2e42`

### Test Results

| Test | Status | Result |
|------|--------|--------|
| **1. Token Statistics** | ✅ PASS | 90 → 64 tools, 80.1% savings |
| **2. Quick Fetch** | ✅ PASS | 25 tokens (vs ~3000 raw) |
| **3. Semantic Search** | ✅ PASS | Found relevant tools for all queries |
| **4. Lazy Loading** | ✅ PASS | 58 tools, 67% token savings |
| **5. Context Mode** | ✅ PASS | Store/retrieve working |
| **6. Web Search (SearXNG)** | ✅ PASS | 5 results from Pi5 |
| **7. Web Fetch** | ✅ PASS | Optimized extraction |
| **8. Context Stats** | ✅ PASS | Tracking enabled |

### Detailed Results

```
┌──────────────────────────────────────────────────────────────────┐
│ TOKEN STATISTICS                                                  │
├──────────────────────────────────────────────────────────────────┤
│  Original tools:       90                                          │
│  Trimmed tools:      64                                          │
│  Token savings:       80.1%                                       │
│  Est. original:       13,500 tokens                               │
│  Est. trimmed:        2,685 tokens                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ QUICK FETCH                                                      │
├──────────────────────────────────────────────────────────────────┤
│  URL: https://example.com                                        │
│  Title: Example Domain                                           │
│  Tokens used: 25 (vs ~3000 raw HTML)                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ SEMANTIC SEARCH                                                  │
├──────────────────────────────────────────────────────────────────┤
│  Query: 'search the web' → 9 matches (searxng_search #1)        │
│  Query: 'run python code' → 3 matches (run_python_snippet #1)    │
│  Query: 'fetch webpage' → 3 matches (fetch_web_content #1)        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ LAZY LOADING                                                     │
├──────────────────────────────────────────────────────────────────┤
│  Mode: minimal                                                   │
│  Total tools: 58                                                │
│  Token savings: 67%                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ CONTEXT MODE                                                     │
├──────────────────────────────────────────────────────────────────┤
│  Store: Success ✓                                                │
│  Reference: @ctx:default:b38493f6e8f86351                        │
│  Retrieve: Found ✓ (repo: claude-code, stars: 15000)            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ WEB SEARCH (SearXNG via Pi5)                                     │
├──────────────────────────────────────────────────────────────────┤
│  Query: 'MCP token optimization 2025'                            │
│  Results: 5                                                       │
│  - Dramatically Reducing AI Agent Token Usage with MC...         │
│  - MCP Token Optimization: 4 Approaches Compared                  │
│  - 10 strategies to reduce MCP token bloat                       │
└──────────────────────────────────────────────────────────────────┘
```

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      LLM (Claude)                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │ tools/list   │  │ tools/call  │  │ tools_minimal│
     │ (64 schemas) │  │ (execution) │  │ (summaries)  │
     └──────────────┘  └──────────────┘  └──────────────┘
              │               │               │
              ▼               ▼               ▼
     ┌─────────────────────────────────────────────────────────┐
     │                  MCP Server                              │
     │  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
     │  │ Trimmed    │  │ Web Fetch  │  │ Context    │       │
     │  │ Schemas    │  │ Optimized  │  │ Mode       │       │
     │  │ (64 tools) │  │ (markdown) │  │ (SQLite)   │       │
     │  └────────────┘  └────────────┘  └────────────┘       │
     └─────────────────────────────────────────────────────────┘
```

---

## Essential MCP Servers for Developers

We recommend these additional MCP servers to complement our 83 tools:

### Must-Have (⭐)

| Server | Description | Setup |
|--------|-------------|-------|
| **GitHub** | Repository management, issues, PRs | `npx -y @modelcontextprotocol/server-github` |
| **Memory** | Persistent knowledge across sessions | `npx -y @modelcontextprotocol/server-memory` |
| **Sentry** | Error tracking and debugging | `npx -y @modelcontextprotocol/server-sentry` |

### Recommended

| Server | Description | Setup |
|--------|-------------|-------|
| **Cloudflare** | Workers, KV, R2, D1 | `npx -y @modelcontextprotocol/server-cloudflare` |
| **Slack** | Channel messaging | `npx -y @modelcontextprotocol/server-slack` |
| **PostgreSQL** | Database queries | `npx -y @modelcontextprotocol/server-postgres` |

### Example Configuration

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-c", "from mcp_server.server import run; run()"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sentry"]
    }
  }
}
```

See [`ESSENTIAL_MCP_SERVERS.md`](ESSENTIAL_MCP_SERVERS.md) for complete list (30+ servers).

---

## Troubleshooting
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
