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
echo "Services:"
echo "  MCP Server:  localhost:7710"
echo "  PostgreSQL:  localhost:5432"
echo "  Redis:       localhost:6379"
echo ""
echo "Remote (Pi5):"
echo "  SearXNG:    http://$PI5_IP:8080"
echo "  Firecrawl:  http://$PI5_IP:3002"
echo ""
echo "Your Ollama:  localhost:11434"
