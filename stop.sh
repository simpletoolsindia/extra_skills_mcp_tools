#!/bin/bash
# MCP Server Stop Script
# Usage: ./stop.sh

cd "$(dirname "$0")"

echo "Stopping MCP Server and all dependencies..."
docker compose -f docker-compose.local.yml down

echo "✅ All services stopped"
