#!/bin/bash
# MCP Server Installation Script
# Self-Hosted Local LLM Tool Ecosystem
#
# Port Sequence (7711 onwards):
#   7711 - SearXNG (Web Search)
#   7712 - Firecrawl (Optional - requires 6 CPU + 12GB RAM)
#   7713 - LiteLLM (LLM Gateway)
#   7714 - PostgreSQL
#   7715 - Redis
#
# All tools are self-hosted by default (no external APIs required)

set -e

echo "=== MCP Server Installation (Self-Hosted) ==="
echo
echo "Port Configuration:"
echo "  7711 - SearXNG (Web Search)"
echo "  7712 - Firecrawl (Optional - Heavy: 6CPU + 12GB RAM)"
echo "  7713 - LiteLLM (LLM Gateway)"
echo "  7714 - PostgreSQL"
echo "  7715 - Redis"
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker not found. SearXNG (web search) won't work without it.${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    echo
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
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
    echo -e "${RED}Error: pip3 or uv is required${NC}"
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

# Install Playwright browsers
echo "Checking Playwright..."
if python3 -c "import playwright" 2>/dev/null; then
    echo "Installing Playwright Chromium browser..."
    playwright install chromium || echo -e "${YELLOW}Note: Playwright browser install may require sudo${NC}"
else
    echo "Playwright not installed (optional - for JS-heavy pages)"
fi

# ========================================================================
# Self-Hosted Service Setup
# ========================================================================

setup_searxng() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found - skipping SearXNG setup${NC}"
        return
    fi

    echo
    echo "=== SearXNG Setup (Port 7711) ==="
    echo "Privacy-respecting search engine, no external API needed."
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

    # Start SearXNG on port 7711
    docker run -d \
        -p 7711:8080 \
        -v "$(pwd)/searxng-data:/etc/searxng" \
        --name searxng \
        searxng/searxng

    echo -e "${GREEN}SearXNG started on port 7711${NC}"
}

setup_litellm() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found - skipping LiteLLM setup${NC}"
        return
    fi

    echo
    echo "=== LiteLLM Setup (Port 7713) ==="
    echo "Local LLM gateway for Ollama, vLLM, and other local models."
    echo

    read -p "Start LiteLLM via Docker? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    # Create litellm config
    mkdir -p litellm-config
    cat > litellm-config/config.yaml << 'EOF'
model_list:
  - model_name: ollama-llama3
    litellm_params:
      model: ollama/llama3
      api_base: http://localhost:11434
      stream: true

  - model_name: ollama-mistral
    litellm_params:
      model: ollama/mistral
      api_base: http://localhost:11434
      stream: true

litellm_settings:
  drop_params: true
  set_verbose: true
EOF

    # Stop existing container if any
    docker stop litellm 2>/dev/null || true
    docker rm litellm 2>/dev/null || true

    # Start LiteLLM on port 7713
    docker run -d \
        -p 7713:8000 \
        -v "$(pwd)/litellm-config:/app/config.yaml" \
        --name litellm \
        -e DATABASE_URL=sqlite:///litellm.db \
        -e LITELLM_MASTER_KEY=sk-local \
        ghcr.io/berriai/litellm:main

    echo -e "${GREEN}LiteLLM started on port 7713${NC}"
}

setup_firecrawl() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found - skipping Firecrawl setup${NC}"
        return
    fi

    echo
    echo "=== Firecrawl Setup (Port 7712) - OPTIONAL ==="
    echo -e "${YELLOW}WARNING: Firecrawl requires heavy resources!${NC}"
    echo "  - 6 CPU cores minimum"
    echo "  - 12GB RAM minimum"
    echo "  - Good for servers with resources, NOT for Pi5"
    echo
    echo "Lightweight alternative (already installed):"
    echo "  - Playwright: for JS-heavy pages"
    echo "  - Scrapling: fast CSS extraction"
    echo "  - Webclaw: article extraction"
    echo

    read -p "Start Firecrawl anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Firecrawl. Using lightweight scrapers instead."
        return
    fi

    # Create firecrawl-data directory
    mkdir -p firecrawl-data

    # Stop existing container if any
    docker stop firecrawl 2>/dev/null || true
    docker rm firecrawl 2>/dev/null || true

    # Check system resources
    CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo "0")
    TOTAL_MEM=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "0")

    echo "Your system: $CPU_CORES CPUs, ${TOTAL_MEM}GB RAM"

    if [ "$CPU_CORES" -lt 6 ] || [ "$TOTAL_MEM" -lt 12 ]; then
        echo -e "${YELLOW}Warning: Your system may not have enough resources for Firecrawl${NC}"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping Firecrawl."
            return
        fi
    fi

    # Pull and start Firecrawl
    echo "Starting Firecrawl (this may take a while)..."
    docker pull ghcr.io/mendableai/firecrawl/main:latest 2>/dev/null || \
    docker pull firecrawl/mcp-server:latest 2>/dev/null || true

    docker run -d \
        -p 7712:3002 \
        -v "$(pwd)/firecrawl-data:/app/data" \
        --name firecrawl \
        -e PORT=3002 \
        -e HOST=0.0.0.0 \
        -e USE_DB_AUTHENTICATION=false \
        firecrawl/mcp-server:latest 2>/dev/null || \
    docker run -d \
        -p 7712:3002 \
        -v "$(pwd)/firecrawl-data:/app/data" \
        --name firecrawl \
        -e PORT=3002 \
        -e HOST=0.0.0.0 \
        ghcr.io/mendableai/firecrawl/main 2>/dev/null || {
        echo -e "${RED}Failed to start Firecrawl. Using lightweight scrapers instead.${NC}"
        return
    }

    echo -e "${GREEN}Firecrawl started on port 7712${NC}"
    echo "Admin UI: http://localhost:7712/admin/CHANGEME/queues"
}

setup_searxng
setup_litellm
setup_firecrawl

# ========================================================================
# Test Installation
# ========================================================================

echo
echo "=== Testing Installation ==="

# Build environment variables
export SEARXNG_BASE_URL=${SEARXNG_BASE_URL:-http://localhost:7711}
export FIRECRAWL_HOST=${FIRECRAWL_HOST:-http://localhost:7712}
export PLAYWRIGHT_HEADLESS=true

python3 -c "
from mcp_server.server import TOOL_CALLABLES
from mcp_server.tools.firecrawl import get_scraper_status

print(f'Success! {len(TOOL_CALLABLES)} tools installed:')
print()

# Show scraper status
status = get_scraper_status()
print('Scraper Status:')
for name, info in status.items():
    if name == 'active_scraper':
        continue
    available = '✓' if info.get('available') else '✗'
    req = info.get('requirements', '')
    print(f'  {available} {name}: {req}')

print(f'  Active: {status[\"active_scraper\"]}')
print()

# Show port configuration
print('Docker Port Configuration:')
print('  7711 - SearXNG (Web Search)')
print('  7712 - Firecrawl (Optional)')
print('  7713 - LiteLLM (LLM Gateway)')
print('  7714 - PostgreSQL')
print('  7715 - Redis')
print()

print('All tools are SELF-HOSTED (no external API keys required for core functionality).')
"

echo
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo
echo "To start the MCP server with all services:"
echo "  source .venv/bin/activate"
echo "  SEARXNG_BASE_URL=http://localhost:7711 FIRECRAWL_HOST=http://localhost:7712 python -m mcp_server"
echo
echo "For Claude Code, add to ~/.claude/settings.json:"
cat << 'CLAUDE'
{
  "mcpServers": {
    "mcp-server": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:7711",
        "FIRECRAWL_HOST": "http://localhost:7712"
      }
    }
  }
}
CLAUDE
echo
echo "Docker services status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -E "searxng|firecrawl|litellm|postgres|redis" || echo "No MCP services running"
