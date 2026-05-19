from fastapi import APIRouter

from app.schemas.dashboard import DashboardLive
from app.websocket.live_energy import hub

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/live", response_model=DashboardLive)
def live_dashboard() -> DashboardLive:
    return hub.state
