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
| SearXNG | 7171 |

### Mac (Local) - `docker-compose.local.yml`
```bash
./start-local.sh
```
| Service | Port |
|---------|------|
| MCP Server | 7710 |
| Firecrawl | 7172 |
| PostgreSQL | 7173 |
| Redis | 7174 |

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

## Architecture

```
┌─────────────────────────────────┐
│           PI5 (Remote)            │
│                                 │
│  SearXNG → :7171               │
└─────────────────────────────────┘
              │
              │ http://PI5_IP:7171
              │
┌─────────────────────────────────┐
│           MAC (Local)            │
│                                 │
│  MCP Server → :7710            │
│  Firecrawl  → :7172            │
│  PostgreSQL → :7173            │
│  Redis      → :7174            │
│  Ollama     → localhost:11434   │
└─────────────────────────────────┘
```

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

## License

MIT
