#!/bin/bash
# Mac / Local Setup - On Demand Services
# Run: ./start-local.sh

set -e

echo "=== Local Setup (Mac) ==="

# Get Remote IP
echo "Enter Remote (Pi5) IP address (check: ping pi5.local):"
read -r REMOTE_IP
REMOTE_IP=${REMOTE_IP:-192.168.1.100}

# Save to .env
cat > .env << EOF
REMOTE_IP=$REMOTE_IP
EOF

echo "Remote IP: $REMOTE_IP"
echo "Building and starting local services..."
docker compose -f docker-compose.local.yml up -d --build

echo ""
echo "=== Local Services Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Services:"
echo "  MCP Server:  localhost:7710 (TCP)"
echo "  PostgreSQL:  localhost:5432"
echo "  Redis:       localhost:6379"
echo ""
echo "Remote (Pi5):"
echo "  SearXNG:    http://$REMOTE_IP:7711"
echo "  Firecrawl:  http://$REMOTE_IP:7712"
echo ""
echo "Your Ollama (host):  localhost:11434"
