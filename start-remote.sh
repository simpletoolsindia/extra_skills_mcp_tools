#!/bin/bash
# Remote (Pi5) Setup - Always On Services
# Run: ./start-remote.sh

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

# Copy .env.example if not exists
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Cloudflare Tunnel (optional - uncomment to enable)
# CLOUDFLARE_TOKEN=your_token_here
EOF
fi

echo "Starting remote services..."
docker compose -f docker-compose.remote.yml up -d

echo ""
echo "=== Remote Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Local Access:"
echo "  SearXNG:   http://localhost:7711"
echo "  Firecrawl: http://localhost:7712"
echo ""
echo "Enable Cloudflare: Uncomment CLOUDFLARE_TOKEN in .env"
