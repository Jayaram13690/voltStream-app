from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardLive
from app.websocket.live_energy import hub

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/live", response_model=DashboardLive)
def live_dashboard(_db: Session = Depends(get_db)) -> DashboardLive:
    del _db
    return hub.state
