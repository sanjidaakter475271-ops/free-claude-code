# Use Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install free-claude-code from GitHub
RUN pip install --no-cache-dir \
    git+https://github.com/Alshahryar1/free-claude-code.git

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

# Copy source code (if needed)
COPY . .

# Set environment
ENV PYTHONPATH=/app/src:$PYTHONPATH
ENV PORT=7860
EXPOSE 7860

# Start fcc-server
CMD ["fcc-server", "--host", "0.0.0.0", "--port", "7860"]
