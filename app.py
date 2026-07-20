"""Entry point for Railway/Hugging Face."""

import sys
import os

# Add src to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import the FastAPI app factory and services
from free_claude_code.api.app import create_app
from free_claude_code.api.ports import ApiServices

# Create services and app
services = ApiServices()
fastapi_app = create_app(services)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
