#!/bin/bash
# Local (Mac) Setup - On Demand Services
# Run this on your Mac

set -e

echo "=== Local Setup (Mac) ==="

# Get Pi5 IP
echo "Enter Pi5 IP address (check: ping pi5.local):"
read -r PI5_IP
PI5_IP=${PI5_IP:-192.168.1.100}

# Save to .env
cat > .env << EOF
PI5_IP=$PI5_IP
EOF

echo "Pi5 IP: $PI5_IP"
echo "Building and starting local services..."
docker-compose up -d --build

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
echo "  SearXNG:    http://$PI5_IP:7711"
echo "  Firecrawl:  http://$PI5_IP:7712"
echo ""
echo "Your Ollama (host):  localhost:11434"
