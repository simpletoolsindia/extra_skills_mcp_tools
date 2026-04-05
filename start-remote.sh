#!/bin/bash
# Remote (Pi5) Setup - Always On Services
# Run this on Pi5

set -e

echo "=== Remote Setup (Pi5) ==="

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

# Create Firecrawl data dir
mkdir -p firecrawl-data

# Cloudflare token
if [ ! -f .env ]; then
    echo "Enter Cloudflare Tunnel Token (from dash.cloudflare.com):"
    read -r TOKEN
    echo "CLOUDFLARE_TOKEN=$TOKEN" > .env
fi

echo "Starting remote services..."
docker-compose -f docker-compose.remote.yml up -d

echo ""
echo "=== Remote Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Local Access:"
echo "  SearXNG:   http://localhost:7711"
echo "  Firecrawl: http://localhost:7712"
echo ""
echo "Remote Access:"
echo "  Via Cloudflare Tunnel (check .env)"
