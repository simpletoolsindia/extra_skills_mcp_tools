# MCP Unified Server — 86 Tools for Agentic AI

> **Split Setup** | Pi5 (Remote) + Mac (Local)

---

## Two Docker Compose Files

### Pi5 (Remote) - `docker-compose.remote.yml`
```bash
./start-remote.sh
```
| Service | Port |
|---------|------|
| SearXNG | 8080 |
| Firecrawl | 3002 |

### Mac (Local) - `docker-compose.local.yml`
```bash
./start-local.sh
```
| Service | Port |
|---------|------|
| MCP Server | 7710 |
| PostgreSQL | 5432 |
| Redis | 6379 |

---

## Setup

### Pi5
```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start-remote.sh
```

### Mac
```bash
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
./start-local.sh
# Enter Pi5 IP when asked
```

---

## Remote Services URL (Update in .env)

Pi5 IP: `192.168.1.100` (example)

```env
PI5_IP=192.168.1.100
```

MCP connects to:
- `http://PI5_IP:8080` (SearXNG)
- `http://PI5_IP:3002` (Firecrawl)

---

## Commands

### Pi5
```bash
# Start
docker compose -f docker-compose.remote.yml up -d

# Stop
docker compose -f docker-compose.remote.yml down
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

## Architecture

```
┌─────────────────────────────────┐
│           PI5 (Remote)            │
│                                 │
│  SearXNG  → :8080               │
│  Firecrawl → :3002              │
│                                 │
│  (You manage domain routing)     │
└─────────────────────────────────┘
              │
              │ http://PI5_IP:8080
              │
┌─────────────────────────────────┐
│           MAC (Local)            │
│                                 │
│  MCP Server → :7710             │
│  PostgreSQL → :5432             │
│  Redis      → :6379             │
│  Ollama     → localhost:11434   │
└─────────────────────────────────┘
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

## Notes

- **Pi5:** Runs 24/7, low power
- **Mac:** Uses power only when needed
- **Firecrawl:** Requires 6 CPU + 12GB RAM
- **Ollama:** Already on Mac (localhost:11434)

---

## License

MIT
