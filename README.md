# MCP Unified Server — 86 Tools for Agentic AI

> **Split Setup** | Pi5 (Remote) + Mac (Local)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         PI5 (Always On)                       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │
│  │   SearXNG   │  │  Firecrawl  │  │  Cloudflare     │     │
│  │   :7711     │  │   :7712     │  │  Tunnel         │     │
│  └─────────────┘  └─────────────┘  └─────────────────┘     │
│                                                              │
│  Low power (~5W), runs 24/7                                  │
└──────────────────────────────────────────────────────────────┘
              │ HTTP                              │
              ▼                                   ▼
┌──────────────────────────────────────────────────────────────┐
│                         MAC (On Demand)                       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ MCP Server  │  │ PostgreSQL  │  │    Redis    │          │
│  │   :7710     │  │   :5432     │  │   :6379     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐                           │
│  │  Ollama     │  │  Playwright │                          │
│  │ localhost   │  │  (browser)  │                           │
│  └─────────────┘  └─────────────┘                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Setup

### 1. Pi5 (Run Once)

```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start-remote.sh

# Enter Cloudflare Tunnel Token (get from dash.cloudflare.com)
```

### 2. Mac (Run Once)

```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start-local.sh

# Enter Pi5 IP (e.g., 192.168.1.100)
```

---

## Services

### Pi5 (Always On)

| Service | Port | Description | Remote |
|---------|------|-------------|--------|
| **SearXNG** | 7711 | Web search | ✅ Cloudflare |
| **Firecrawl** | 7712 | Smart scraping | ✅ Cloudflare |

### Mac (On Demand)

| Service | Port | Description |
|---------|------|-------------|
| **MCP Server** | 7710 | 86 tools (TCP) |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6379 | Cache |
| **Ollama** | 11434 | Your LLM (host) |
| **Playwright** | - | Browser |

---

## Commands

### Pi5
```bash
# Start
docker-compose -f docker-compose.remote.yml up -d

# Stop
docker-compose -f docker-compose.remote.yml down

# Logs
docker-compose -f docker-compose.remote.yml logs -f
```

### Mac
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f mcp-server
```

---

## Remote Access

### Via Cloudflare (Pi5 Services)
Access SearXNG/Firecrawl from anywhere via Cloudflare URL.

### Via SSH Tunnel (Full Access)
```bash
# Tunnel MCP port to Mac
ssh -L 7710:localhost:7710 pi@pi5.local
```

### Claude Code
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

| Category | Tools |
|----------|-------|
| 🌐 Web Search | 4 |
| 📖 Web Scraping | 10 |
| 📰 News & Research | 14 |
| 🐙 GitHub | 6 |
| 💻 Code Execution | 4 |
| 📊 Data & Charts | 11 |
| 📺 YouTube | 6 |
| 🧠 Intelligence | 17 |
| 💾 Files | 9 |
| 🔧 Research | 5 |

---

## Environment Variables

### Pi5 (.env)
```env
CLOUDFLARE_TOKEN=your_cloudflare_tunnel_token
```

### Mac (.env)
```env
PI5_IP=192.168.1.100
```

---

## Power Usage

| Machine | Services | Power |
|---------|----------|-------|
| Pi5 | SearXNG, Firecrawl | ~5W |
| Mac | MCP, Postgres, Redis | Only when running |

**Result:** Pi5 stays on 24/7 (cheap), Mac only uses power when you work.

---

## License

MIT

⭐ **Star on GitHub!**
