#!/bin/bash
# MCP Server Installation Script
# Local LLM Tool Ecosystem with Playwright, Scrapling, Freedium & Code Sandbox

set -e

echo "=== MCP Server Installation ==="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker not found. SearXNG (web search) won't work without it.${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    echo
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for uv (fast Python package manager)
if command -v uv &> /dev/null; then
    echo -e "${GREEN}Using uv for package management${NC}"
    USE_UV=1
elif command -v pip3 &> /dev/null; then
    echo "Using pip3"
    USE_UV=0
else
    echo "Error: pip3 or uv is required"
    exit 1
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    if command -v uv &> /dev/null; then
        uv venv .venv
    else
        python3 -m venv .venv
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [ "$USE_UV" = "1" ]; then
    uv pip install -e .
else
    python3 -m pip install -e .
fi

# Install Playwright browsers (if playwright is installed)
echo "Checking Playwright..."
if python3 -c "import playwright" 2>/dev/null; then
    echo "Installing Playwright Chromium browser..."
    playwright install chromium || echo "Note: Playwright browser install may require sudo"
else
    echo "Playwright not installed (optional - for JS-heavy pages)"
fi

# Setup SearXNG Docker (optional)
setup_searxng() {
    if ! command -v docker &> /dev/null; then
        echo "Docker not found - skipping SearXNG setup"
        return
    fi

    echo
    echo "=== SearXNG Setup (Optional) ==="
    echo "This enables web_search functionality"
    echo

    read -p "Start SearXNG via Docker? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    # Create searxng-data directory
    mkdir -p searxng-data

    # Create settings.yml
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
  secret_key: "mcp-server-search-key-change-in-production"
  limiter: false
EOF

    # Create limiter.toml
    cat > searxng-data/limiter.toml << 'EOF'
[botdetection]
trusted_proxies = ['127.0.0.0/8', '::1']

[botdetection.ip_limit]
filter_link_local = false
link_token = false

[botdetection.ip_lists]
pass_ip = ['127.0.0.0/8', '::1']
EOF

    # Stop existing container if any
    docker stop searxng 2>/dev/null || true
    docker rm searxng 2>/dev/null || true

    # Start SearXNG
    docker run -d \
        -p 8888:8080 \
        -v "$(pwd)/searxng-data:/etc/searxng" \
        --name searxng \
        searxng/searxng

    echo "SearXNG started at http://localhost:8888"
}

setup_searxng

# Test installation
echo
echo "=== Testing Installation ==="
SEARXNG_BASE_URL=http://localhost:8888 PLAYWRIGHT_HEADLESS=true python3 -c "
from mcp_server.server import TOOL_CALLABLES
print(f'Success! {len(TOOL_CALLABLES)} tools installed:')
for name in TOOL_CALLABLES.keys():
    print(f'  - {name}')
"

echo
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo
echo "To start the MCP server:"
echo "  SEARXNG_BASE_URL=http://localhost:8888 python -m mcp_server"
echo
echo "Or activate venv and run:"
echo "  source .venv/bin/activate"
echo "  SEARXNG_BASE_URL=http://localhost:8888 mcp-server"
echo
echo "For Claude Code, add to ~/.claude/settings.json:"
echo '  "mcpServers": { "mcp-server": { "command": "/path/to/python", "args": ["-m", "mcp_server"], "env": { "SEARXNG_BASE_URL": "http://localhost:8888" }}}'