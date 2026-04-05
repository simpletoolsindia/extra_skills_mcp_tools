#!/bin/bash
# MCP Server - One Command Setup

set -e

echo "=== MCP Server Setup ==="

# Create SearXNG config directory and files
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
  secret_key: "mcp-server-key-change-in-production"
  limiter: false
EOF

cat > searxng-data/limiter.toml << 'EOF'
[botdetection]
trusted_proxies = ['127.0.0.0/8', '::1']
[botdetection.ip_lists]
pass_ip = ['127.0.0.0/8', '::1']
EOF

echo "Config created."

# Build and start all containers
echo "Building and starting containers..."
docker-compose up -d --build

echo ""
echo "=== All Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Services:"
echo "  MCP Server:    mcp-server (container)"
echo "  SearXNG:       http://localhost:7711"
echo "  LiteLLM:       http://localhost:7713"
echo "  PostgreSQL:    localhost:7714"
echo "  Redis:         localhost:7715"
echo ""
echo "To stop:"
echo "  docker-compose down"
