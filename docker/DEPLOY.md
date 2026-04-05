# MCP Unified Server - Pi5 Deployment Guide

## Overview

Deploy SearXNG + MCP Server on your Pi5 using Dokploy.

**URLs:**
- Search: https://search.sridharhomelab.in
- API: https://api.sridharhomelab.in

## Prerequisites

- Raspberry Pi 5 or similar SBC
- Docker & Docker Compose installed
- Domain DNS pointing to your Pi5 IP
- SSL certificates (Let's Encrypt recommended)

## Quick Deploy

### 1. Clone the repository
```bash
cd /opt
git clone https://github.com/simpletoolsindia/extra_skills_mcp_tools.git
cd extra_skills_mcp_tools
```

### 2. Generate SSL Certificates

Using Let's Encrypt (recommended):
```bash
# Install certbot
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d search.sridharhomelab.in --agree-tos --email your@email.com -n

# Copy certificates
sudo cp /etc/letsencrypt/live/search.sridharhomelab.in/fullchain.pem docker/nginx/certs/cert.pem
sudo cp /etc/letsencrypt/live/search.sridharhomelab.in/privkey.pem docker/nginx/certs/key.pem
sudo chmod 644 docker/nginx/certs/*.pem
```

### 3. Configure Environment
```bash
# Create .env file
cat > .env << 'EOF'
SEARXNG_BASE_URL=https://search.sridharhomelab.in
GITHUB_TOKEN=your_github_token_here
HF_TOKEN=your_huggingface_token_here
EOF
```

### 4. Deploy with Docker Compose
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f searxng
```

### 5. Verify Deployment
```bash
# Test SearXNG
curl https://search.sridharhomelab.in/search?q=test&format=json

# Test health endpoint
curl https://search.sridharhomelab.in/health
```

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| SearXNG | https://search.sridharhomelab.in | Web search |
| LiteLLM | https://api.sridharhomelab.in | LLM gateway |
| Health | https://search.sridharhomelab.in/health | Health check |

## Updating

```bash
cd /opt/extra_skills_mcp_tools
git pull
docker-compose down
docker-compose up -d
```

## Troubleshooting

### SearXNG not responding
```bash
# Check logs
docker-compose logs searxng

# Restart
docker-compose restart searxng
```

### SSL certificate issues
```bash
# Check certificate files exist
ls -la docker/nginx/certs/

# Regenerate if needed
sudo certbot certonly --standalone -d search.sridharhomelab.in --agree-tos --email your@email.com -n --force-renewal
```

### Pi5 Performance
```bash
# Check resource usage
docker stats

# Limit memory if needed (add to docker-compose.yml)
# mem_limit: 512m
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                │
│   search.sridharhomelab.in  │  api.sridharhomelab.in    │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
   ┌────▼────┐              ┌──────▼──────┐
   │ SearXNG │              │   LiteLLM   │
   │ :8080   │              │    :8000    │
   └─────────┘              └─────────────┘
        │                           │
   ┌────▼────┐              ┌──────▼──────┐
   │  Redis  │              │  PostgreSQL │
   │ :6379   │              │    :5432    │
   └─────────┘              └─────────────┘
```

## MCP Server Configuration

Add to Claude Code `settings.local.json`:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/usr/bin/python3",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "https://search.sridharhomelab.in",
        "PYTHONPATH": "/opt/extra_skills_mcp_tools/src"
      }
    }
  }
}
```

## Security Notes

1. Change default secrets in `limiter.toml` and `litellm-config/config.yaml`
2. Use strong passwords for PostgreSQL
3. Enable firewall: `sudo ufw allow 443/tcp`
4. Regular backups of `searxng-data/` and `postgres-data/`

## Support

- GitHub Issues: https://github.com/simpletoolsindia/extra_skills_mcp_tools/issues