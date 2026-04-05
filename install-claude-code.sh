#!/bin/bash
# MCP Server Suite - Claude Code Installation Script
# Run: ./install-claude-code.sh
# This script configures Claude Code with MCP servers

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     MCP Server Suite - Claude Code Installation             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# CHECK REQUIREMENTS
# =============================================================================

echo "Checking requirements..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found. Install from: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker found: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"

# Check Node.js (for NPX MCPs)
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}→${NC} Node.js not found. Installing knowledgegraph-mcp via Docker instead..."
    USE_DOCKER_KG=1
else
    echo -e "${GREEN}✓${NC} Node.js found: $(node --version)"
    USE_DOCKER_KG=0
fi

# =============================================================================
# GET CONFIGURATION
# =============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get Pi5 IP
echo "Enter Pi5 IP address (or press Enter for default 192.168.0.2):"
read -r PI5_IP
PI5_IP=${PI5_IP:-192.168.0.2}

# Save to .env
cat > .env << EOF
PI5_IP=$PI5_IP
SEARXNG_BASE_URL=https://search.sridharhomelab.in
EOF

echo -e "${GREEN}✓${NC} Pi5 IP: $PI5_IP"
echo -e "${GREEN}✓${NC} SearXNG: https://search.sridharhomelab.in"
echo ""

# =============================================================================
# STEP 1: Start Docker Services
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}STEP 1:${NC} Starting Docker Services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker compose -f docker-compose.local.yml up -d --build

echo -e "${GREEN}✓${NC} Docker services started"
echo ""

# =============================================================================
# STEP 2: Clone Additional MCP Servers
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}STEP 2:${NC} Installing Additional MCP Servers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create mcp-servers directory
mkdir -p mcp-servers

# Clone knowledgegraph-mcp (memory & knowledge graph)
if [ ! -d "mcp-servers/knowledgegraph-mcp" ]; then
    echo "Cloning knowledgegraph-mcp..."
    git clone https://github.com/n-r-w/knowledgegraph-mcp.git mcp-servers/knowledgegraph-mcp 2>/dev/null
    echo -e "${GREEN}✓${NC} knowledgegraph-mcp installed"
else
    echo -e "${YELLOW}→${NC} knowledgegraph-mcp already exists"
fi

# Build knowledgegraph-mcp Docker image if no Node.js
if [ "$USE_DOCKER_KG" = "1" ]; then
    cd mcp-servers/knowledgegraph-mcp
    if [ ! -f "knowledgegraph-mcp" ]; then
        echo "Building knowledgegraph-mcp Docker image..."
        docker build -t knowledgegraph-mcp . 2>/dev/null || echo -e "${YELLOW}→${NC} Docker build skipped"
    fi
    cd ../..
fi

echo ""

# =============================================================================
# STEP 3: Configure Claude Code
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}STEP 3:${NC} Configuring Claude Code..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SETTINGS_FILE="$HOME/.claude/settings.json"
BACKUP_FILE="$HOME/.claude/settings.json.backup-$(date +%Y%m%d-%H%M%S)"

# Backup existing settings
if [ -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓${NC} Backed up settings to $BACKUP_FILE"
fi

# Create MCP server config based on Node.js availability
if [ "$USE_DOCKER_KG" = "1" ]; then
    # Use Docker for knowledgegraph-mcp
    cat > "$SETTINGS_FILE" << EOF
{
  "env": {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-c", "from mcp_server.server import run; run()"]
    },
    "knowledge-graph": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "knowledgegraph-mcp"]
    },
    "sequential-thinking": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "ghcr.io/modelcontextprotocol/server-sequential-thinking"]
    }
  },
  "hasCompletedOnboarding": true,
  "skipDangerousModePermissionPrompt": true
}
EOF
else
    # Use NPX
    cat > "$SETTINGS_FILE" << EOF
{
  "env": {
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "mcpServers": {
    "mcp-server": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "-c", "from mcp_server.server import run; run()"]
    },
    "knowledge-graph": {
      "command": "npx",
      "args": ["-y", "knowledgegraph-mcp"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  },
  "hasCompletedOnboarding": true,
  "skipDangerousModePermissionPrompt": true
}
EOF
fi

echo -e "${GREEN}✓${NC} Claude Code configured with MCP servers"
echo ""

# =============================================================================
# SUMMARY
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}📋 MCP Servers Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🐳 Docker Services:"
docker ps --format "  • {{.Names}} : {{.Status}}" 2>/dev/null | grep -E "mcp|searxng|firecrawl|postgres|redis" | head -10 || true
echo ""
echo "💻 Claude Code MCPs:"
echo "   • mcp-server         - 83 tools (Web Search, GitHub, YouTube, etc.)"
echo "   • knowledge-graph    - SQLite-backed persistent memory"
echo "   • sequential-thinking - Structured problem solving"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code: claude"
echo "2. Type /help to see available MCP tools"
echo ""
