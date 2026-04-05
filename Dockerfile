FROM python:3.12-slim

WORKDIR /app

# Install system deps for playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Install Playwright browsers
RUN playwright install chromium --with-deps

ENV PYTHONUNBUFFERED=1
ENV SEARXNG_BASE_URL=http://searxng:8080

# Run MCP server
CMD ["python", "-m", "mcp_server"]
