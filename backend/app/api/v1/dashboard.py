from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.websocket.live_energy import hub

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/live")
async def live_dashboard(since: float = Query(None, description="Timestamp for change detection")) -> dict:
    """
    Polling endpoint for live dashboard data with auto-tick.
    
    Args:
        since: Optional timestamp to check if data has changed since last poll
    
    Returns:
        Dict with 'changed' flag, 'timestamp', and 'data' if changed
    """
    return hub.get_state(since=since, auto_tick=True)


# @router.get("/live-stream")
# async def live_dashboard_stream():
#     """
#     Legacy SSE endpoint - may not work with Lambda + API Gateway
#     Kept for backward compatibility but polling is recommended
#     <!-- SSE (Server-Sent Events) are not used in this project. The application uses WebSocket for real-time updates. -->
#     """
#     return StreamingResponse(hub.generate_sse(), media_type="text/event-stream")