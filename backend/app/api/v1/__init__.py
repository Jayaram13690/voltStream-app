from fastapi import APIRouter

from app.api.v1 import analytics, billing, dashboard, devices, chat

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(devices.router)
api_router.include_router(billing.router)
api_router.include_router(chat.router)
