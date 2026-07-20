"""Entry point for Railway/Hugging Face with admin panel enabled."""

import sys
import os

# Add src to Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Monkeypatch admin panel to allow remote access with auth
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Store original before importing app
_original_admin_check = None

try:
    from free_claude_code.api.admin_routes import router as admin_router
    # Find and patch the admin local-only check
    for route in admin_router.routes:
        if hasattr(route, 'endpoint'):
            original_endpoint = route.endpoint
            def patched_endpoint(request: Request, *args, **kwargs):
                # Allow remote access with basic auth
                auth_header = request.headers.get('authorization', '')
                if not auth_header:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Admin panel requires authentication",
                        headers={"WWW-Authenticate": "Basic"},
                    )
                return original_endpoint(request, *args, **kwargs)
            route.endpoint = patched_endpoint
except Exception:
    pass

# Try to import from src/free_claude_code directly
try:
    from free_claude_code.api.app import create_app
    from free_claude_code.api.ports import ApiServices
    from dataclasses import dataclass
    from typing import Any

    @dataclass
    class MockRequestRuntime:
        def current_settings(self):
            class Settings:
                log_api_error_tracebacks = False
                anthropic_auth_token = os.environ.get("ANTHROPIC_API_KEY", "")
                openai_api_key = os.environ.get("OPENAI_API_KEY", "")
                gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
                default_model = os.environ.get("DEFAULT_MODEL", "claude-sonnet-4-20250514")
                max_tokens = int(os.environ.get("MAX_TOKENS", "8192"))
                temperature = float(os.environ.get("TEMPERATURE", "0.7"))

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

    # Add basic auth middleware for admin panel
    from starlette.middleware.base import BaseHTTPMiddleware

    ADMIN_USERNAME = "root"
    ADMIN_PASSWORD = "nazmulhassan.baf"

    class AdminAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if request.url.path.startswith("/admin"):
                auth_header = request.headers.get("authorization", "")
                if not auth_header.startswith("Basic "):
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Admin authentication required"},
                        headers={"WWW-Authenticate": "Basic"},
                    )
                import base64
                try:
                    decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
                    username, password = decoded.split(":", 1)
                    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
                        return JSONResponse(
                            status_code=401,
                            content={"detail": "Invalid credentials"},
                            headers={"WWW-Authenticate": "Basic"},
                        )
                except Exception:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid authentication"},
                        headers={"WWW-Authenticate": "Basic"},
                    )
            response = await call_next(request)
            return response

    from fastapi.responses import JSONResponse
    fastapi_app.add_middleware(AdminAuthMiddleware)

except Exception as e:
    print(f"Failed to create app: {e}", flush=True)
    raise RuntimeError("Could not create FastAPI app")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
