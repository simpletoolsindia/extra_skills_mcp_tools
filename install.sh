#!/bin/bash
# MCP Server Installation Script
# Self-Hosted Local LLM Tool Ecosystem
#
# All tools are self-hosted:
# - SearXNG: Privacy-respecting web search
# - Firecrawl: Intelligent web scraping
# - Playwright: Headless browser automation
# - Scrapling: Fast CSS-based extraction
# - LiteLLM: Local LLM gateway
# - Plus 80+ additional tools

set -e

echo "=== MCP Server Installation (Self-Hosted) ==="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker not found. Self-hosted services (SearXNG, Firecrawl) won't work without it.${NC}"
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
# Self-Hosted Service Setup (SearXNG, Firecrawl)
# ========================================================================

setup_searxng() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found - skipping SearXNG setup${NC}"
        return
    fi

    echo
    echo "=== SearXNG Setup (Self-Hosted Web Search) ==="
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

    # Start SearXNG
    docker run -d \
        -p 8888:8080 \
        -v "$(pwd)/searxng-data:/etc/searxng" \
        --name searxng \
        searxng/searxng

    echo -e "${GREEN}SearXNG started at http://localhost:8888${NC}"
}

setup_firecrawl() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found - skipping Firecrawl setup${NC}"
        return
    fi

    echo
    echo "=== Firecrawl Setup (Self-Hosted Web Scraping) ==="
    echo "Intelligent content extraction with JS rendering support."
    echo

    read -p "Start Firecrawl via Docker? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    # Create firecrawl-data directory
    mkdir -p firecrawl-data

    # Stop existing container if any
    docker stop firecrawl 2>/dev/null || true
    docker rm firecrawl 2>/dev/null || true

    # Start Firecrawl
    docker run -d \
        -p 3002:3002 \
        -v "$(pwd)/firecrawl-data:/app/data" \
        --name firecrawl \
        -e PORT=3002 \
        -e HOST=0.0.0.0 \
        -e LOG_LEVEL=info \
        firecrawl/mcp-server:latest 2>/dev/null || \
    docker run -d \
        -p 3002:3002 \
        -v "$(pwd)/firecrawl-data:/app/data" \
        --name firecrawl \
        ghcr.io/mendableai/firecrawl:main 2>/dev/null || \
    echo -e "${YELLOW}Firecrawl image not available. Using local scrapers as fallback.${NC}"

    if docker ps | grep -q firecrawl; then
        echo -e "${GREEN}Firecrawl started at http://localhost:3002${NC}"
    fi
}

setup_searxng
setup_firecrawl

# ========================================================================
# Test Installation
# ========================================================================

echo
echo "=== Testing Installation ==="

# Build environment variables
export SEARXNG_BASE_URL=${SEARXNG_BASE_URL:-http://localhost:8888}
export FIRECRAWL_HOST=${FIRECRAWL_HOST:-http://localhost:3002}
export PLAYWRIGHT_HEADLESS=true

python3 -c "
from mcp_server.server import TOOL_CALLABLES
print(f'Success! {len(TOOL_CALLABLES)} tools installed:')
print()

# Group tools by category
categories = {
    'Search': ['searxng_search', 'search_images', 'search_news', 'searxng_health'],
    'Scraping': ['fetch_web_content', 'scrape_dynamic', 'extract_structured', 'scrape_freedium',
                 'firecrawl_scrape', 'firecrawl_crawl', 'webclaw_crawl', 'webclaw_extract_article',
                 'browserbase_browse'],
    'News': ['hackernews_top', 'hackernews_new', 'hackernews_best', 'hackernews_ask',
             'hackernews_show', 'hackernews_get_comments', 'hackernews_user'],
    'Research': ['wikipedia_search', 'wikipedia_get_article', 'wikipedia_related',
                 'youtube_transcript', 'youtube_transcript_timed', 'youtube_search',
                 'youtube_video_info', 'youtube_batch_transcribe', 'youtube_summarize',
                 'research_start', 'research_add_source', 'research_complete',
                 'analyze_problem', 'thinking_session_create', 'thinking_step'],
    'Code': ['run_code', 'run_python_snippet', 'test_code_snippet', 'run_command'],
    'Data': ['pandas_create', 'pandas_filter', 'pandas_aggregate', 'pandas_correlation',
             'pandas_outliers', 'plot_line', 'plot_bar', 'plot_pie', 'plot_scatter',
             'plot_histogram', 'generate_chart_spec'],
    'Files': ['file_read', 'file_write', 'file_list', 'file_info', 'file_search',
              'markitdown_html_to_md', 'markitdown_url_to_md', 'markitdown_file_to_md'],
    'GitHub': ['github_repo', 'github_readme', 'github_issues', 'github_commits',
               'github_search_repos', 'github_file_content'],
    'HuggingFace': ['huggingface_search_models', 'huggingface_search_datasets',
                    'huggingface_model_info', 'huggingface_trending'],
    'Intelligence': ['engi_task_classify', 'engi_repo_scope_find', 'engi_flow_summarize',
                     'engi_bug_trace', 'engi_implementation_plan', 'engi_poc_plan',
                     'engi_impact_analyze', 'engi_test_select', 'engi_doc_context_build',
                     'engi_doc_update_plan', 'engi_memory_checkpoint', 'engi_memory_restore'],
}

for cat, tools in categories.items():
    available = [t for t in tools if t in TOOL_CALLABLES]
    if available:
        print(f'{cat} ({len(available)}): {', '.join(available[:3])}{'...' if len(available) > 3 else ''}')

print()
print('All tools are SELF-HOSTED (no external API keys required for core functionality).')
print('Optional cloud services: GitHub API (free tier), HuggingFace (free tier)')
"

echo
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo
echo "To start the MCP server with all self-hosted services:"
echo "  source .venv/bin/activate"
echo "  SEARXNG_BASE_URL=http://localhost:8888 FIRECRAWL_HOST=http://localhost:3002 python -m mcp_server"
echo
echo "For Claude Code, add to ~/.claude/settings.json:"
cat << 'CLAUDE'
{
  "mcpServers": {
    "mcp-server": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:8888",
        "FIRECRAWL_HOST": "http://localhost:3002"
      }
    }
  }
}
CLAUDE
echo
echo "Docker services status:"
docker ps --filter "name=searxng" --filter "name=firecrawl" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not running or no services started"
