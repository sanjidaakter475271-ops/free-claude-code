# Use Python 3.11 to avoid StrEnum and forward reference issues
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    sed \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies directly (no requirements.txt needed)
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
    tenacity

# Copy source code
COPY . .

# ========== AUTO FIX ALL PYTHON COMPATIBILITY ISSUES ==========

# Fix 1: Add "from __future__ import annotations" to all Python files in src/
RUN find /app/src -name "*.py" -exec sh -c \
    'echo "from __future__ import annotations" | cat - "$1" > /tmp/tmpfile && mv /tmp/tmpfile "$1"' _ {} \;

# Fix 2: Fix Python 2 except syntax: "except A, B:" → "except (A, B):"
RUN find /app/src -name "*.py" -exec sed -i \
    's/except \([A-Za-z_][A-Za-z0-9_]*\), \([A-Za-z_][A-Za-z0-9_]*\):/except (\1, \2):/g' {} +

# Add src to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

EXPOSE 7860

CMD ["python", "app.py"]
