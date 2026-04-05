# MCP Unified Server — 86 Tools for Agentic AI

> **Split Setup** | Pi5 (Remote) + Mac (Local) | Docker Compose

---

## Two Separate Docker Compose Files

### 1. `docker-compose.remote.yml` — Pi5 (Always On)

```bash
docker compose -f docker-compose.remote.yml up -d
```

**Services:**
| Service | Port | Description |
|---------|------|-------------|
| SearXNG | 7711 | Web search |
| Firecrawl | 7712 | Smart scraping |

### 2. `docker-compose.local.yml` — Mac (On Demand)

```bash
docker compose -f docker-compose.local.yml up -d
```

**Services:**
| Service | Port | Description |
|---------|------|-------------|
| MCP Server | 7710 | 86 tools (TCP) |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |

---

## Setup

### Pi5
```bash
# Clone
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# Setup
chmod +x start-remote.sh
./start-remote.sh
```

### Mac
```bash
# Clone
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools

# Setup
chmod +x start-local.sh
./start-local.sh
# Enter Pi5 IP when asked
```

---

## Architecture

```
┌─────────────────────────────────────┐
│            PI5 (Always On)            │
│                                     │
│  ┌───────────┐  ┌───────────┐      │
│  │  SearXNG  │  │ Firecrawl │      │
│  │   :7711   │  │   :7712   │      │
│  └───────────┘  └───────────┘      │
└─────────────────────────────────────┘
              │
              │ HTTP
              ▼
┌─────────────────────────────────────┐
│              MAC (On Demand)        │
│                                     │
│  ┌───────────┐  ┌───────────┐      │
│  │MCP Server │  │ PostgreSQL│      │
│  │   :7710   │  │   :5432   │      │
│  └───────────┘  └───────────┘      │
│                                     │
│  ┌───────────┐  ┌───────────┐      │
│  │   Redis  │  │  Ollama   │      │
│  │   :6379  │  │   :11434  │      │
│  └───────────┘  └───────────┘      │
└─────────────────────────────────────┘
```

---

## Commands

### Pi5
```bash
# Start
docker compose -f docker-compose.remote.yml up -d

# Stop
docker compose -f docker-compose.remote.yml down

# Logs
docker compose -f docker-compose.remote.yml logs -f
```

### Mac
```bash
# Start
docker compose -f docker-compose.local.yml up -d

# Stop
docker compose -f docker-compose.local.yml down

# Logs
docker compose -f docker-compose.local.yml logs -f mcp-server
```

---

## Remote Access (Pi5 → Mac)

```bash
# SSH tunnel MCP port to Mac
ssh -L 7710:localhost:7710 pi@pi5.local
```

---

## Claude Code (Mac)

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

| Category | Count |
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

### Mac (.env)
```env
REMOTE_IP=192.168.1.100  # Your Pi5 IP
```

---

## Notes

- **Pi5:** Runs 24/7, low power (~5W)
- **Mac:** Uses power only when running
- **Firecrawl:** Requires 6 CPU + 12GB RAM
- **Ollama:** Already running on Mac (localhost:11434)

---

## License

MIT

⭐ **Star on GitHub!**
