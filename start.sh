#!/bin/bash
# MCP Server - One Command Setup

set -e

echo "=== MCP Server Setup ==="

# 1. Create SearXNG config
mkdir -p searxng-data
cat > searxng-data/settings.yml << 'EOF'
use_default_settings: true
general:
  instance_name: "MCP Server"
search:
  safe_search: 0
  formats:
    - html
    - json
server:
  secret_key: "mcp-server-key-change-me"
  limiter: false
EOF

cat > searxng-data/limiter.toml << 'EOF'
[botdetection]
trusted_proxies = ['127.0.0.0/8', '::1']
[botdetection.ip_lists]
pass_ip = ['127.0.0.0/8', '::1']
EOF

# 2. Create nginx config
mkdir -p nginx/conf.d
cat > nginx/nginx.conf << 'EOF'
worker_processes auto;
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    gzip on;
    upstream searxng_backend {
        server searxng:8080;
    }
    include /etc/nginx/conf.d/*.conf;
}
EOF

cat > nginx/conf.d/search.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://searxng_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        add_header Access-Control-Allow-Origin "*";
    }

    location /search {
        proxy_pass http://searxng_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        add_header Access-Control-Allow-Origin "*";
    }
}
EOF

# 3. Install Python dependencies
if ! command -v python3 &> /dev/null; then
    echo "Python3 required. Installing MCP server only (no Docker services)..."
else
    pip install -e . 2>/dev/null || python3 -m pip install -e .
fi

# 4. Start Docker services
echo "Starting Docker services..."
cd docker
docker-compose up -d

echo ""
echo "=== Done! ==="
echo ""
echo "Services:"
echo "  SearXNG (Search): http://localhost:7711"
echo "  LiteLLM (LLM):    http://localhost:7713"
echo "  PostgreSQL:        localhost:7714"
echo "  Redis:            localhost:7715"
echo ""
echo "To run MCP Server:"
echo "  source .venv/bin/activate"
echo "  SEARXNG_BASE_URL=http://localhost:7711 python -m mcp_server"
echo ""
