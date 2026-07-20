# Use Python 3.14
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    sed \
    && rm -rf /var/lib/apt/lists/*

# Install free-claude-code from YOUR fork
RUN pip install --no-cache-dir \
    git+https://github.com/sanjidaakter475271-ops/free-claude-code.git

# Install additional dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    loguru \
    huggingface-hub==0.23.5 \
    pydantic \
    pydantic-settings \
    tiktoken \
    httpx \
    python-dotenv \
    anthropic \
    openai \
    aiohttp \
    tenacity \
    jsonschema \
    jinja2 \
    starlette

# Copy source code
COPY . .

# Patch admin panel to allow remote access with auth
# Find and replace local-only checks in installed package
RUN find /usr/local/lib -path "*/free_claude_code/*" -name "*.py" -exec grep -l "127.0.0.1\|localhost\|local-only" {} + 2>/dev/null | while read f; do \
    sed -i 's/127\.0\.0\.1/0.0.0.0/g; s/localhost/0.0.0.0/g; s/local-only/public/g' "$f"; \
    done || true

# Set environment
ENV PORT=7860
ENV HOST=0.0.0.0
EXPOSE 7860

# Start fcc-server with public host
CMD ["sh", "-c", "fcc-server --host 0.0.0.0 --port ${PORT:-7860}"]
