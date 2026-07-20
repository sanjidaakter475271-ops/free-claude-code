"""Entry point for Railway/Hugging Face."""

import sys
import os

# Add src to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import the actual FastAPI app
from free_claude_code.api.app import app as fastapi_app

if __name__ == "__main__":
    import uvicorn
    # Use PORT from environment (Railway/HF), default 7860
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
