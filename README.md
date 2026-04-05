# MCP Unified Server — 86 Tools for Agentic AI

> Self-hosted MCP server with 86 tools for local LLMs (Qwen, Gemma, DeepSeek, GLM, Claude, GPT)

---

## Prerequisites

- Docker & Docker Compose installed
- 8GB+ RAM recommended
- macOS or Linux

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
```

---

## Step 2: Configure Environment

Edit the `.env` file (or create it):

```bash
# Optional: Set Pi5 IP if using remote SearXNG
PI5_IP=192.168.1.100
SEARXNG_BASE_URL=http://192.168.1.100:7171
```

**Note:** If not using Pi5, the local SearXNG at port 7171 will be used automatically.

---

## Step 3: Create SearXNG Configuration

```bash
mkdir -p searxng-data
cat > searxng-data/settings.yml << 'EOF'
use_default_settings: true
general:
  instance_name: "MCP Server Search"
search:
  safe_search: 0
  formats:
    - html
    - json
server:
  secret_key: "change-me-in-production"
  limiter: false
EOF
```

---

## Step 4: Start Services

```bash
# Build and start all containers
docker compose -f docker-compose.local.yml up -d --build

# Or use the convenience script (prompts for Pi5 IP)
./start-local.sh
```

---

## Step 5: Verify Installation

Check all containers are running:

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE          STATUS
mcp-server    mcp-server     Up X minutes
searxng       searxng/...    Up X minutes
firecrawl     mcp/firecrawl  Up X minutes
postgres      postgres:15     Up X minutes
redis         redis:7         Up X minutes
```

---

## Step 6: Test the Tools

### Test Web Search
```bash
docker exec mcp-server python -c "
from mcp_server.tools.web_search import web_search
result = web_search('hello world', limit=3)
print(result)
"
```

### Test Hacker News
```bash
docker exec mcp-server python -c "
from mcp_server.tools.hackernews import get_top_stories
result = get_top_stories(limit=3)
print(result)
"
```

### Test GitHub
```bash
docker exec mcp-server python -c "
from mcp_server.tools.github import search_repositories
result = search_repositories(query='python', limit=3)
print(result)
"
```

### Test YouTube
```bash
docker exec mcp-server python -c "
from mcp_server.tools.youtube_transcript import get_transcript_from_url
result = get_transcript_from_url(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
print(result)
"
```

---

## Step 7: Connect to Claude Code

Add to your Claude Code config (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-c", "from mcp_server.server import run; run()"]
    }
  }
}
```

Or use TCP mode (port 7710):

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MCP_SERVER_PORT": "7710",
        "SEARXNG_BASE_URL": "http://localhost:7171"
      }
    }
  }
}
```

---

## Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| MCP Server | 7710 | Main MCP protocol server (TCP mode available) |
| SearXNG | 7171 | Self-hosted web search |
| Firecrawl | 7172 | Web scraping service |
| PostgreSQL | 7173 | Database |
| Redis | 7174 | Cache |

---

## All 86 Tools

| Category | Count | Examples |
|----------|-------|----------|
| 🌐 Web Search | 14 | searxng_search, search_images, search_news |
| 📖 Web Scraping | 7 | fetch_web_content, scrape_dynamic, firecrawl_scrape |
| 📰 News | 7 | hackernews, search_news, get_article |
| 🐙 GitHub | 5 | search_repositories, get_repo, list_commits |
| 💻 Code Execution | 4 | run_command, execute_sandboxed |
| 📊 Charts | 6 | create_chart, create_line_chart, create_bar_chart |
| 📺 YouTube | 5 | get_transcript, search_youtube, summarize_transcript |
| 📚 Wikipedia | 2 | search_wikipedia, get_article |
| 💾 Files | 5 | list_directory, read_file, write_file |
| 🔧 Other | 31 | intelligence, research, sequential_thinking |

---

## Common Commands

```bash
# View logs
docker compose -f docker-compose.local.yml logs -f mcp-server

# Restart a specific service
docker compose -f docker-compose.local.yml restart mcp-server

# Stop all services
docker compose -f docker-compose.local.yml down

# Rebuild after code changes
docker compose -f docker-compose.local.yml up -d --build
```

---

## Troubleshooting

### SearXNG returns 403
- Ensure `searxng-data/settings.yml` has `limiter: false`
- Restart SearXNG: `docker compose restart searxng`

### Wikipedia rate limited
- Wikipedia API may block rapid requests
- Use alternative search tools instead

### MCP Server won't start
- Check logs: `docker compose logs mcp-server`
- Ensure port 7710 is not in use

---

## Architecture

```
┌─────────────────────────────────────────┐
│           MAC (Local Machine)           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │     Docker Containers           │   │
│  │                                 │   │
│  │  MCP Server  → :7710 (TCP)      │   │
│  │  SearXNG     → :7171            │   │
│  │  Firecrawl   → :7172            │   │
│  │  PostgreSQL  → :7173            │   │
│  │  Redis       → :7174            │   │
│  └─────────────────────────────────┘   │
│                  ↕                      │
│         Claude Code / LLM              │
└─────────────────────────────────────────┘
```

---

## License

MIT
