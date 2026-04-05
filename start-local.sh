#!/bin/bash
# Mac / Local Setup - On Demand Services
# Run: ./start-local.sh

set -e

echo "=== Mac Local Setup ==="

# Get Pi5 IP
echo "Enter Pi5 IP address:"
read -r PI5_IP
PI5_IP=${PI5_IP:-192.168.1.100}

# Save to .env
cat > .env << EOF
PI5_IP=$PI5_IP
EOF

echo "Pi5 IP: $PI5_IP"
echo ""
echo "Starting local services..."
docker compose -f docker-compose.local.yml up -d --build

echo ""
echo "=== Local Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Local Ports:"
echo "  7710 - MCP Server"
echo "  7173 - PostgreSQL"
echo "  7174 - Redis"
echo ""
echo "Remote Ports (Pi5):"
echo "  7171 - SearXNG"
echo "  7172 - Firecrawl"
echo ""
echo "Your Ollama: localhost:11434"
