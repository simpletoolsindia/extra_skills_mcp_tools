#!/bin/bash
# Pi5 Setup - Always On Services
# Run this on your Pi5

set -e

echo "=== Pi5 MCP Services Setup ==="

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

echo "Config created."

# Start services
echo "Starting services..."
docker-compose -f docker-compose.pi5.yml up -d

echo ""
echo "=== Pi5 Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Local Access:"
echo "  SearXNG:    http://pi5.local:7711"
echo "  PostgreSQL: pi5.local:7714"
echo "  Redis:      pi5.local:7715"
echo ""
echo "Remote Access:"
echo "  Cloudflare tunnel must be configured"
echo "  Set CLOUDFLARE_TOKEN in .env file"
echo ""
echo "To stop:"
echo "  docker-compose -f docker-compose.pi5.yml down"
