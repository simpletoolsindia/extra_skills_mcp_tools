#!/bin/bash
# MCP Server Startup Script
# Usage: ./start.sh

set -e

echo "=========================================="
echo "  MCP Server Startup"
echo "=========================================="

# Change to script directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Start all services
echo ""
echo "🚀 Starting MCP Server and dependencies..."
docker compose -f docker-compose.local.yml up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(mcp-server|postgres|redis|chromadb)" || true

# Test MCP server
echo ""
echo "🔧 Testing MCP Server..."
TOOL_COUNT=$(docker exec -i mcp-server python -c "from mcp_server.server import TOOL_CALLABLES; print(len(TOOL_CALLABLES))" 2>/dev/null || echo "0")
if [ "$TOOL_COUNT" -gt 0 ]; then
    echo "✅ MCP Server: $TOOL_COUNT tools loaded"
else
    echo "⚠️  MCP Server: Tools not responding (may still be starting)"
fi

# Test SearXNG connectivity
echo ""
echo "🔍 Testing SearXNG (Pi5)..."
SEARXNG_RESULT=$(curl -s --max-time 5 "https://search.sridharhomelab.in/search?q=test&format=json" 2>/dev/null | jq -r '.number_of_results' 2>/dev/null || echo "error")
if [ "$SEARXNG_RESULT" != "error" ] && [ "$SEARXNG_RESULT" != "" ]; then
    echo "✅ SearXNG: $SEARXNG_RESULT results found"
else
    echo "⚠️  SearXNG: Not reachable (check Pi5 is on)"
fi

echo ""
echo "=========================================="
echo "  Startup Complete!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - MCP Server: http://localhost:7710"
echo "  - PostgreSQL: localhost:7173"
echo "  - Redis: localhost:7174"
echo "  - ChromaDB: localhost:8000"
echo "  - SearXNG: https://search.sridharhomelab.in"
echo ""
echo "To stop: docker compose -f docker-compose.local.yml down"
