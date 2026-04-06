# MCP Server Suite — Token-Optimized AI Development Platform

> **Self-hosted MCP server with 83+ tools for AI workflows** — featuring **80%+ token reduction** through 5 optimization layers.

[![GitHub stars](https://img.shields.io/github/stars/simpletoolsindia/extra_skills_mcp_tools)](https://github.com/simpletoolsindia/extra_skills_mcp_tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Token Optimization (80%+ Savings)](#token-optimization-80-savings)
- [Claude Code Optimization](#claude-code-optimization)
- [All Tools (100+)](#all-tools-100)
- [Architecture](#architecture)
- [Essential MCP Servers](#essential-mcp-servers)
- [Docker Services](#docker-services)
- [Installation](#installation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

This MCP server provides **83+ tools** for AI-powered development workflows, featuring:

- **🌐 Web Search & Scraping** — SearXNG, Firecrawl, structured extraction
- **🐙 GitHub Integration** — Repos, issues, commits, search
- **📺 YouTube** — Transcripts, search, summarization
- **💻 Code Execution** — Python sandbox, testing
- **📊 Data & Charts** — Pandas, matplotlib visualization
- **🧠 Engineering Intelligence** — Task classification, bug tracing, memory
- **⚡ Token Optimization** — Built-in 80% token reduction

**No API keys required** for core functionality.

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

# 4. Verify installation
docker compose -f docker-compose.local.yml ps
```

---

## Token Optimization (80% Savings)

This server implements **5 layers of token optimization** to maximize your context window:

### Optimization Layers

| Layer | Reduction | Description |
|-------|-----------|-------------|
| **Tool Trimming** | 80% | 90 → 64 tools with concise descriptions |
| **Web Content** | 80-97% | Clean markdown, strip nav/ads/scripts |
| **Context Mode** | 98% | External SQLite storage for outputs |
| **Lazy Loading** | 91% | Load schemas on-demand |
| **Semantic Search** | 91% | Natural language tool discovery |

### Token Comparison

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Tool List | ~13,500 tokens | ~2,700 tokens | **80%** |
| Web Fetch | ~8,000 tokens | ~2,000 tokens | **75%** |
| Tool Output | ~5,000 tokens | ~50 tokens | **98%** |
| Full Workflow | ~200,000 tokens | ~30,000 tokens | **85%** |

### Optimization Tools

| Tool | Usage | Tokens |
|------|-------|--------|
| `quick_fetch` | Ultra-fast title + summary | ~25-300 |
| `fetch_web_content` | Clean markdown with tracking | ~2,000 |
| `fetch_structured` | Article/product/table | ~1,500 |
| `ctx_store_output` | Store output externally | ~50 |
| `tools_minimal` | List without full schemas | ~2,000 |
| `semantic_search` | "search the web" → searxng_search | ~500 |

### Usage Examples

```python
# Before: Fetch raw HTML (~8000 tokens)
fetch("https://example.com")  # Returns bloated HTML

# After: Optimized fetch (~300 tokens)
quick_fetch(url="https://example.com", max_tokens=1500)
# Returns: {title: "Example", summary: "...", tokens: 300}

# Store large outputs externally (98% reduction)
ctx_store_output(
    tool_name="github_repo",
    arguments={"owner": "anthropics"},
    output={"repo": "claude-code", "stars": 15000}
)
# Returns: {"ref": "@ctx:default:abc123", "size_bytes": 54}
# Instead of storing 500+ tokens, just store the reference
```

---

## Claude Code Optimization

### Model Selection Strategy

**Use the right model for the right task:**

| Model | Best For | Cost | When to Use |
|-------|----------|------|-------------|
| **Sonnet** | Most coding | $3/1M tokens | Default choice, ~60% cheaper |
| **Haiku** | Code review, docs | $0.25/1M tokens | Routine tasks, fixes |
| **Opus** | Complex refactoring | $15/1M tokens | Architecture, deep debugging |

### Recommended Settings

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Model Settings
claude config set --claude-code-subagent-model sonnet
export HAIKU_MODEL=haiku

# Thinking Token Limit (~70% savings)
# Default: 32,000 tokens
# Recommended: 10,000 tokens
export MAX_THINKING_TOKENS=10000

# Compaction Settings (better performance)
# Default: 95% context before compact
# Recommended: 50% for more working room
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50

# MCP Server Limit
# Keep under 10 MCP servers, 80 total tools
# More = reduced effective context window
```

### Quick Commands

| Command | Purpose |
|---------|---------|
| `/cost` | Monitor token usage and costs |
| `/clear` | Free context reset between tasks |
| `/compact` | Manual compaction at breakpoints |
| `/context` | Check current context usage |

### MCP Server Best Practices

> **Warning:** Each MCP server adds tool definitions to context. Excessive servers reduce effective context from 200k to ~70k.

**Recommended:** Keep under **10 MCP servers**, **80 total tools**.

### 10 Strategies to Reduce MCP Token Bloat

1. **Design tools with intent** — Single purpose, clear inputs/outputs
2. **Cache aggressively** — Identical queries hit cache
3. **Minimize server usage at runtime** — Enable only when needed
4. **Group tools by domain** — Logical grouping reduces confusion
5. **Deploy subagents** — Route routine tasks to Haiku
6. **Just-in-time context loading** — Load schemas on-demand
7. **Externalize computational results** — Store large outputs
8. **Apply advanced data filtering** — Filter at extraction time
9. **Externalize cross-cutting concerns** — Centralize auth/errors
10. **Keep tools lean** — Runtime handles concerns centrally

### Cost Comparison

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| 1 hour coding | $2.50 | $0.75 | **70%** |
| 1 day research | $8.00 | $2.40 | **70%** |
| 1 week project | $35.00 | $10.50 | **70%** |

---

## All Tools (100+)

### 🌐 Web Search & Scraping (10)

| Tool | Description |
|------|-------------|
| `searxng_search` | Web search via SearXNG (Pi5) |
| `search_images` | Image search |
| `search_news` | News search |
| `searxng_health` | Check SearXNG status |
| `fetch_web_content` | Clean markdown extraction |
| `fetch_structured` | Article/product/table extraction |
| `quick_fetch` | Ultra-fast title + summary |
| `scrape_dynamic` | JavaScript-heavy pages (Playwright) |
| `firecrawl_scrape` | Advanced scraping |
| `webclaw_extract_article` | Article extraction |

### 🐙 GitHub (6)

| Tool | Description |
|------|-------------|
| `github_repo` | Repository information |
| `github_readme` | README content |
| `github_issues` | List issues |
| `github_commits` | List commits |
| `github_search_repos` | Search repositories |
| `github_file_content` | Get file content |

### 📺 YouTube (6)

| Tool | Description |
|------|-------------|
| `youtube_transcript` | Get transcript |
| `youtube_transcript_timed` | Timestamped transcript |
| `youtube_search` | Search videos |
| `youtube_video_info` | Video metadata |
| `youtube_batch_transcribe` | Batch transcription |
| `youtube_summarize` | Summarize transcript |

### 📰 Hacker News (6)

| Tool | Description |
|------|-------------|
| `hackernews_top` | Top stories |
| `hackernews_new` | Newest stories |
| `hackernews_best` | Best stories |
| `hackernews_ask` | Ask HN |
| `hackernews_show` | Show HN |
| `hackernews_get_comments` | Get comments |

### 💻 Code Execution (4)

| Tool | Description |
|------|-------------|
| `run_code` | Sandboxed execution (Python/JS/Bash) |
| `run_python_snippet` | Python with common imports |
| `test_code_snippet` | Test code output |

### 📊 Data & Charts (11)

| Tool | Description |
|------|-------------|
| `pandas_create` | Create DataFrame |
| `pandas_filter` | Filter data |
| `pandas_aggregate` | Aggregate/group data |
| `pandas_correlation` | Compute correlation |
| `pandas_outliers` | Detect outliers |
| `plot_line` | Line chart |
| `plot_bar` | Bar chart |
| `plot_pie` | Pie chart |
| `plot_scatter` | Scatter plot |
| `plot_histogram` | Histogram |
| `generate_chart_spec` | Ant Design spec |

### 🧠 Engineering Intelligence (17)

| Tool | Description |
|------|-------------|
| `engi_task_classify` | Classify task type |
| `engi_repo_scope_find` | Find relevant files |
| `engi_flow_summarize` | Get execution flow |
| `engi_bug_trace` | Pinpoint bug causes |
| `engi_implementation_plan` | Generate implementation plan |
| `engi_poc_plan` | Scaffold POC |
| `engi_impact_analyze` | Estimate blast radius |
| `engi_test_select` | Select minimum tests |
| `engi_doc_context_build` | Build documentation |
| `engi_doc_update_plan` | Plan docs updates |
| `engi_memory_checkpoint` | Save task state |
| `engi_memory_restore` | Restore checkpoint |
| `thinking_session_create` | Create thinking session |
| `thinking_step` | Add reasoning step |
| `thinking_summary` | Get summary |
| `analyze_problem` | Structured analysis |

### ⚡ Optimization Tools (14)

| Tool | Description |
|------|-------------|
| `get_token_stats` | Token optimization stats |
| `quick_fetch` | Minimal token fetch |
| `fetch_web_content` | Optimized extraction |
| `fetch_structured` | Structured extraction |
| `fetch_with_selectors` | CSS selector extraction |
| `ctx_store_output` | Store output externally |
| `ctx_get_output` | Retrieve stored output |
| `ctx_search` | Search stored outputs |
| `ctx_session_overview` | Session summary |
| `ctx_stats` | Context mode stats |
| `tools_minimal` | Lazy tool list |
| `tools_describe` | Load schemas on-demand |
| `tools_search` | Search tools |
| `semantic_search` | Natural language search |

### 💾 Files & HuggingFace (10)

| Tool | Description |
|------|-------------|
| `file_read` | Read file |
| `file_write` | Write file |
| `file_list` | List directory |
| `file_search` | Search files |
| `huggingface_search_models` | Search models |
| `huggingface_search_datasets` | Search datasets |
| `huggingface_model_info` | Model info |
| `huggingface_trending` | Trending models |
| `markitdown_html_to_md` | HTML → Markdown |
| `markitdown_url_to_md` | URL → Markdown |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Code                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  MCP Servers (< 10 recommended)                            │  │
│  │                                                            │  │
│  │  • mcp-server (83 tools) → Port 7710                    │  │
│  │  • github (10 tools) → NPX                               │  │
│  │  • memory (5 tools) → NPX                                 │  │
│  │  • sentry (5 tools) → NPX                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Services (Local)                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ MCP Server   │  │ PostgreSQL   │  │ Redis        │         │
│  │ :7710        │  │ :7173       │  │ :7174        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ ChromaDB     │  │ Firecrawl    │                           │
│  │ :8000        │  │ :7172        │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Remote (Pi5)                                  │
│                                                                  │
│  ┌──────────────┐                                               │
│  │ SearXNG      │                                               │
│  │ :7171        │                                               │
│  │ (Search API) │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Token Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Before Optimization                           │
│                                                                  │
│  Tool Schemas: 90 tools × 150 tokens = 13,500 tokens           │
│  Web Fetch: ~8,000 tokens per page                             │
│  Tool Outputs: Full JSON in context                            │
│  Total: ~200,000 tokens per session                            │
└─────────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────────┐
│                    After Optimization                            │
│                                                                  │
│  Tool Schemas: 64 tools × 42 tokens = 2,700 tokens (-80%)    │
│  Web Fetch: Quick fetch with token budget = ~300 tokens (-96%)│
│  Tool Outputs: External reference = ~50 tokens (-98%)            │
│  Total: ~30,000 tokens per session (-85%)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Essential MCP Servers

We recommend these additional MCP servers for maximum productivity:

### Must-Have (⭐⭐⭐)

| Server | Description | Setup |
|--------|-------------|-------|
| **GitHub** | Repository, issues, PRs, commits | `npx -y @modelcontextprotocol/server-github` |
| **Memory** | Persistent knowledge across sessions | `npx -y @modelcontextprotocol/server-memory` |
| **Sentry** | Error tracking and debugging | `npx -y @modelcontextprotocol/server-sentry` |

### Recommended (⭐⭐)

| Server | Description | Setup |
|--------|-------------|-------|
| **Cloudflare** | Workers, KV, R2, D1 | `npx -y @modelcontextprotocol/server-cloudflare` |
| **Slack** | Channel messaging | `npx -y @modelcontextprotocol/server-slack` |
| **PostgreSQL** | Database queries | `npx -y @modelcontextprotocol/server-postgres` |
| **Puppeteer** | Browser automation | `npx -y @modelcontextprotocol/server-puppeteer` |

### Complete Configuration

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
    },
    "cloudflare": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-cloudflare"]
    }
  }
}
```

**Total tools:** ~110 tools across 5 servers

---

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| **MCP Server** | 7710 | Main MCP protocol server (83 tools) |
| **SearXNG** | 7171 | Self-hosted web search (Pi5) |
| **Firecrawl** | 7172 | Advanced web scraping |
| **PostgreSQL** | 7173 | Database for persistence |
| **Redis** | 7174 | Cache and job queue |
| **ChromaDB** | 8000 | Vector database for RAG |

---

## Installation

### Prerequisites

- Docker & Docker Compose
- Node.js (optional, for NPX MCPs)
- Pi5 IP (for remote SearXNG, optional)

### Steps

```bash
# 1. Clone
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# 2. Run installer (follow prompts)
./install-claude-code.sh

# 3. Enter Pi5 IP when prompted (default: 192.168.0.2)
#    Or press Enter to skip (SearXNG will be unavailable)

# 4. Restart Claude Code
claude

# 5. Verify
docker compose -f docker-compose.local.yml ps
```

### Manual Setup

```bash
# Start Docker services
docker compose -f docker-compose.local.yml up -d

# Add to ~/.claude/settings.json
cat >> ~/.claude/settings.json << 'EOF'
{
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-c", "from mcp_server.server import run; run()"]
    }
  }
}
EOF
```

---

## Configuration

### Environment Variables

```bash
# Pi5 (Remote) SearXNG
export SEARXNG_BASE_URL=https://your-pi5-ip:7171

# Local Ollama (optional)
export OLLAMA_BASE_URL=http://localhost:11434

# PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=7173
export POSTGRES_DB=mcp_server
export POSTGRES_USER=mcp_user
export POSTGRES_PASSWORD=postgres

# Redis
export REDIS_HOST=localhost
export REDIS_PORT=7174

# Claude Code Optimization
export MAX_THINKING_TOKENS=10000
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50
```

### Pi5 (Remote) Setup

For remote SearXNG on Pi5:

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

# Quick restart
./start.sh    # Start
./stop.sh     # Stop
```

---

## Testing

```bash
# Test token optimization
docker exec mcp-server python -c "
from src.mcp_server.server import _get_token_stats
import json
print(json.dumps(_get_token_stats(), indent=2))
"

# Test web search
docker exec mcp-server python -c "
from src.mcp_server.tools.searxng import search
print(search('MCP token optimization', limit=3))
"

# Test web fetch
docker exec mcp-server python -c "
from src.mcp_server.tools.web_fetch_optimized import quick_fetch
result = quick_fetch('https://example.com', max_tokens=500)
print(f'Title: {result[\"title\"]}')
print(f'Tokens: {result[\"tokens_used\"]}')
"

# Test MCP via network
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_token_stats","arguments":{}},"id":1}' | nc localhost 7710
```

---

## Troubleshooting

### SearXNG returns 403

```bash
# Ensure Pi5 SearXNG has limiter disabled
ssh pi5 "docker exec searxng sed -i 's/limiter: true/limiter: false/' /etc/searxng/settings.yml && docker restart searxng"
```

### SSL Certificate Error

```bash
# Rebuild MCP server (includes ca-certificates)
docker compose -f docker-compose.local.yml up -d --build mcp-server
```

### ChromaDB Connection Error

```bash
# Check and restart
docker compose restart chromadb
```

### High Token Usage

1. Use `/cost` to monitor
2. Enable only needed MCP servers
3. Use `quick_fetch` instead of `fetch_web_content`
4. Store large outputs with `ctx_store_output`
5. Compact at 50% with `/compact`

---

## Documentation

| Document | Description |
|----------|-------------|
| `README.md` | This file |
| `TOKEN_OPTIMIZATION.md` | Technical implementation details |
| `OPTIMIZATION_GUIDE.md` | Claude Code settings & strategies |
| `ESSENTIAL_MCP_SERVERS.md` | Curated MCP server list |

---

## Research Sources

- [Speakeasy Dynamic Toolsets](https://www.speakeasy.com/blog/how-we-reduced-token-usage-by-100x-dynamic-toolsets-v2) — 91-97% reduction
- [Scott Spence Optimization](https://scottspence.com/posts/optimising-mcp-server-context-usage-in-claude-code) — 60% reduction
- [Firecrawl Token Optimization](https://www.firecrawl.dev/blog/best-web-extraction-tools) — 97.9% HTML reduction
- [Mintlify Token Guide](https://www.mintlify.com/affaan-m/everything-claude-code/guides/token-optimization) — 70% cost reduction
- [The New Stack - 10 Strategies](https://thenewstack.io/how-to-reduce-mcp-token-bloat/) — Architecture patterns
- [Context Mode MCP](https://news.ycombinator.com/item?id=47193064) — 98% output reduction
- [Awesome MCP Servers](https://github.com/raoufchebri/awesome-mcp) — Curated server list
- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — Production-ready servers
- [win4r/Awesome-Claude-MCP-Servers](https://github.com/win4r/Awesome-Claude-MCP-Servers) — Claude-optimized

---

## License

MIT License

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=simpletoolsindia/extra_skills_mcp_tools&type=Date)](https://star-history.com/#simpletoolsindia/extra_skills_mcp_tools&type=Date)

---

<p align="center">
  <strong>Built with ❤️ for AI-powered development</strong>
</p>
