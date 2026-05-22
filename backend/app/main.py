import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)

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
handler = Mangum(app)
