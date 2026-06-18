from fastapi import APIRouter

from app.api.v1 import analytics, billing, dashboard, devices, chat, qa, device_agent, energy_advisor
from app.agent.api_router import get_multi_agent_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(devices.router)
api_router.include_router(billing.router)
api_router.include_router(chat.router)
api_router.include_router(qa.router)
api_router.include_router(device_agent.router)
api_router.include_router(energy_advisor.router)

# Add multi-agent router
multi_agent_router = get_multi_agent_router()
api_router.include_router(multi_agent_router)
