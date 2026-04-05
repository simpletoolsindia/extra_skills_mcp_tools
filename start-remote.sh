#!/bin/bash
# Pi5 / Remote Setup - Always On Services
# Run: ./start-remote.sh

set -e

echo "=== Pi5 Remote Setup ==="

# Create SearXNG config
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

cat > searxng-data/limiter.toml << 'EOF'
[botdetection]
trusted_proxies = ['127.0.0.0/8', '::1']
[botdetection.ip_lists]
pass_ip = ['127.0.0.0/8', '::1']
EOF

mkdir -p firecrawl-data

echo "Starting remote services..."
docker compose -f docker-compose.remote.yml up -d

echo ""
echo "=== Remote Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Ports:"
echo "  7171 - SearXNG"
echo "  7172 - Firecrawl"
