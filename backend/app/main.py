from app.core import sqlite_patch

import sqlite3

print("=" * 50)
print("MAIN SQLITE VERSION:", sqlite3.sqlite_version)
print("=" * 50)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    root_path="/prod",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Root endpoint working"}

@app.get("/voltstream-backend")
async def voltstream_backend():
    return {"message": "VoltStream backend route working"}

# Add debug endpoints
@app.get("/debug")
def debug():
    return {
        "status": "debug",
        "message": "Debug endpoint working",
        "routes": [str(route.path) for route in app.routes]
    }

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# Lambda handler
from mangum import Mangum
class DebugMangum(Mangum):
    def __call__(self, event, context):
        print("=" * 80)
        print("EVENT:")
        print(event)
        print("=" * 80)
        return super().__call__(event, context)
    
handler = Mangum(app, api_gateway_base_path="/prod")
