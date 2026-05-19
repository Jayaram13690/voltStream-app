import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.websocket.live_energy import hub


async def _broadcast_loop() -> None:
    while True:
        await asyncio.sleep(2)
        hub.tick()
        await hub.broadcast_snapshot()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_broadcast_loop())
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.websocket("/ws/live-energy")
async def live_energy_ws(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    await hub.broadcast_snapshot()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(websocket)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# Lambda handler
from mangum import Mangum
handler = Mangum(app)