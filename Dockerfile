FROM python:3.12-slim

WORKDIR /app

# Install system deps for playwright, SSL certificates, and yt-dlp
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    netcat-openbsd \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Copy source and install
COPY src ./src
COPY pyproject.toml .

# Install certifi for SSL certificate handling
RUN pip install --no-cache-dir certifi

# Install yt-dlp for YouTube transcripts
RUN pip install --no-cache-dir yt-dlp

# Fix package name for pip
RUN pip install --no-cache-dir -e .

# Install Playwright browsers
RUN playwright install chromium --with-deps

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_HEADLESS=true

# Run MCP server
CMD ["python", "-c", "from mcp_server.server import run; run()"]
