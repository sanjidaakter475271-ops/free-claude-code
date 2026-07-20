"""Entry point for Railway/Hugging Face."""

import sys
import os

# Add src to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Try to import from src/free_claude_code directly
try:
    from free_claude_code.api.app import create_app
    from free_claude_code.api.ports import ApiServices
    from dataclasses import dataclass, field
    from typing import Any, Optional

    @dataclass
    class MockRequestRuntime:
        def current_settings(self):
            class Settings:
                log_api_error_tracebacks = False
                # Add all required settings attributes
                anthropic_auth_token = os.environ.get("ANTHROPIC_API_KEY", "")
                openai_api_key = os.environ.get("OPENAI_API_KEY", "")
                gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
                default_model = os.environ.get("DEFAULT_MODEL", "claude-sonnet-4-20250514")
                max_tokens = int(os.environ.get("MAX_TOKENS", "8192"))
                temperature = float(os.environ.get("TEMPERATURE", "0.7"))

                # Add any other settings attributes that might be needed
                def __getattr__(self, name):
                    return os.environ.get(name.upper(), "")

            return Settings()

    @dataclass  
    class MockAdminRuntime:
        async def apply_admin_config(self, updates): return {}
        def admin_status(self): return {}
        async def test_provider(self, provider_id): return {}
        async def refresh_models(self): return None
        async def request_restart(self): pass

    @dataclass
    class MockTaskController:
        pass

    services = ApiServices(
        requests=MockRequestRuntime(),
        admin=MockAdminRuntime(),
        tasks=MockTaskController()
    )
    fastapi_app = create_app(services)

except Exception as e:
    print(f"Failed to create app: {e}", flush=True)
    raise RuntimeError("Could not create FastAPI app")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
