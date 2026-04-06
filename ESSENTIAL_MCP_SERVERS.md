# Essential MCP Servers for Developers

A curated list of **must-have MCP servers** for developer productivity, organized by category.

> **Note:** Our MCP server already includes 83+ tools. These additional servers complement our setup with specialized integrations.

---

## Categories

1. [Version Control](#version-control)
2. [Databases](#databases)
3. [Cloud & Infrastructure](#cloud--infrastructure)
4. [Monitoring & Observability](#monitoring--observability)
5. [Communication](#communication)
6. [Browser & Web](#browser--web)
7. [Knowledge & Memory](#knowledge--memory)

---

## Version Control

### GitHub MCP ⭐ (Essential)
**Official MCP Server for GitHub**

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

**Tools:** Repository management, issues, PRs, commits, file operations

**Setup:** Requires `GITHUB_TOKEN` environment variable
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### Git MCP
**Local Git operations**

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    }
  }
}
```

**Tools:** Read git history, branches, diffs, commits

---

## Databases

### PostgreSQL MCP
**Direct database queries**

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost:5432/mydb"]
    }
  }
}
```

**Tools:** Query, schema inspection, read-only access

### SQLite MCP
**Local database access**

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"]
    }
  }
}
```

---

## Cloud & Infrastructure

### AWS MCP
**AWS resources management**

```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-aws"]
    }
  }
}
```

**Tools:** S3, EC2, Lambda operations

### Cloudflare MCP ⭐ (Essential)
**Workers, KV, R2, D1**

```json
{
  "mcpServers": {
    "cloudflare": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-cloudflare"]
    }
  }
}
```

**Tools:** Deploy workers, manage KV, R2 buckets, D1 databases

### CircleCI MCP
**Fix CI/CD build failures**

```json
{
  "mcpServers": {
    "circleci": {
      "command": "npx",
      "args": ["-y", "@circleci/server-mcp"]
    }
  }
}
```

**Setup:** Requires `CIRCLECI_API_KEY`

---

## Monitoring & Observability

### Sentry MCP ⭐ (Essential)
**Error tracking and debugging**

```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sentry"]
    }
  }
}
```

**Setup:** Requires `SENTRY_AUTH_TOKEN` and `SENTRY_ORG`

**Tools:** View errors, stack traces, assign issues

### Axiom MCP
**Log analysis and queries**

```json
{
  "mcpServers": {
    "axiom": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-axiom"]
    }
  }
}
```

**Tools:** Query logs, traces, events in natural language

---

## Communication

### Slack MCP
**Channel management and messaging**

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"]
    }
  }
}
```

**Setup:** Requires `SLACK_BOT_TOKEN`

**Tools:** Post messages, search channels, manage threads

---

## Browser & Web

### Puppeteer MCP
**Browser automation**

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

**Tools:** Screenshot, scrape JS-heavy sites, form filling

### Brave Search MCP
**Private web search**

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"]
    }
  }
}
```

**Setup:** Requires `BRAVE_API_KEY`

---

## Knowledge & Memory

### Memory MCP ⭐ (Essential)
**Persistent knowledge graph**

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Tools:** Store and recall information across sessions

**Example:**
```
Claude: Remember that I prefer TypeScript over JavaScript
Claude: What's my preferred language?
Claude: Based on your memory, you prefer TypeScript over JavaScript.
```

### Obsidian MCP
**Notes and knowledge base**

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"]
    }
  }
}
```

**Setup:** Requires Obsidian vault path

---

## Recommended Starter Pack

For most developers, this combination provides maximum value:

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

**Total tools:** ~100+ tools across all servers

---

## Security Best Practices

### API Token Management

```bash
# Use environment variables, never hardcode tokens
export GITHUB_TOKEN=ghp_xxx
export SENTRY_AUTH_TOKEN=sntrys_xxx
export SLACK_BOT_TOKEN=xoxb-xxx

# Add to ~/.zshrc or ~/.bashrc for persistence
```

### Token Scopes

| Server | Minimum Scope |
|--------|---------------|
| GitHub | repo, read:user |
| Sentry | org:read |
| Slack | channels:read, chat:write |
| Cloudflare | Account permissions only |

---

## MCP Server Comparison

| Server | Stars | Ease | Use Case |
|--------|-------|------|----------|
| GitHub | Official | Easy | All developers |
| Memory | Official | Easy | Long projects |
| Sentry | Official | Easy | Bug tracking |
| Cloudflare | Official | Easy | Serverless |
| PostgreSQL | Official | Medium | Data work |
| Puppeteer | Official | Medium | Web scraping |
| Slack | Official | Easy | Notifications |
| Brave Search | Official | Easy | Private search |

---

## Installation Tips

### Quick Install (npx)
```bash
# Most servers work with npx
npx -y @modelcontextprotocol/server-github
```

### Python Servers (uvx)
```bash
# Install uvx first
pip install uvx

# Then run
uvx mcp-server-git
```

### Docker (for local servers)
```bash
docker run -p 5432:5432 \
  -e POSTGRES_PASSWORD=secret \
  postgres:15
```

---

## Performance Tips

### Keep Under 10 MCP Servers
> Each MCP server adds tool definitions to context. More servers = less effective context.

### Recommended Priority

1. **GitHub** - Code management (essential)
2. **Memory** - Persistence (essential)
3. **Sentry** - Debugging (recommended)
4. **Cloudflare** - Deployment (if using CF)
5. **Slack** - Notifications (optional)
6. **PostgreSQL** - Data queries (if needed)
7. **Puppeteer** - Web scraping (optional)

---

## Sources

- [Awesome MCP Servers](https://github.com/raoufchebri/awesome-mcp)
- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [win4r/Awesome-Claude-MCP-Servers](https://github.com/win4r/Awesome-Claude-MCP-Servers)
- [Model Context Protocol Docs](https://modelcontextprotocol.io)
