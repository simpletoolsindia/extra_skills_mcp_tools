#!/bin/bash
# Mac Setup - MCP Server
# Connects to Pi5 services

set -e

echo "=== Mac MCP Server Setup ==="

# Get Pi5 IP
echo "Enter your Pi5 IP address (or press Enter for 192.168.1.100):"
read -r PI5_IP
PI5_IP=${PI5_IP:-192.168.1.100}

# Save to .env
cat > .env << EOF
PI5_IP=$PI5_IP
EOF

echo "Pi5 IP set to: $PI5_IP"

# Start MCP server
echo "Building and starting MCP server..."
docker-compose up -d --build

echo ""
echo "=== Mac MCP Server Running! ==="
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""
echo "Services:"
echo "  MCP Server:    localhost:7710 (TCP for remote access)"
echo "  Ollama:       localhost:11434 (Mac local)"
echo ""
echo "Pi5 Services:"
echo "  SearXNG:      $PI5_IP:7711"
echo "  PostgreSQL:   $PI5_IP:7714"
echo "  Redis:        $PI5_IP:7715"
echo ""
echo "To stop:"
echo "  docker-compose down"
