"""Entry point for Railway/Hugging Face."""

import sys
import os

# Add src to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Add smoke/lib to path for server.py
SMOKE_LIB = os.path.join(os.path.dirname(__file__), "smoke", "lib")
if SMOKE_LIB not in sys.path:
    sys.path.insert(0, SMOKE_LIB)

# Try to import from smoke/lib/server.py
try:
    from server import app as fastapi_app
except Exception as e1:
    print(f"smoke/lib/server.py failed: {e1}", flush=True)

    # Fallback: Try creating app with factory
    try:
        from free_claude_code.api.app import create_app
        from free_claude_code.api.ports import ApiServices
        from dataclasses import dataclass

        @dataclass
        class MockRequestRuntime:
            def current_settings(self):
                class Settings:
                    log_api_error_tracebacks = False
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

    except Exception as e2:
        print(f"All failed: {e2}", flush=True)
        raise RuntimeError("Could not create FastAPI app")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
