import json
import random

from fastapi import WebSocket

from app.schemas.dashboard import DashboardLive


class LiveEnergyHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._state = DashboardLive(
            grid_usage=4.2,
            solar_generation=6.8,
            battery=82,
            savings=2340.0,
        )

    @property
    def state(self) -> DashboardLive:
        return self._state

    def tick(self) -> DashboardLive:
        g = max(0.0, self._state.grid_usage + random.uniform(-0.35, 0.35))
        s = max(0.0, self._state.solar_generation + random.uniform(-0.6, 0.6))
        b = int(max(0, min(100, self._state.battery + random.randint(-1, 1))))
        sv = max(0.0, self._state.savings + random.uniform(-5, 12))
        self._state = DashboardLive(grid_usage=round(g, 2), solar_generation=round(s, 2), battery=b, savings=round(sv, 2))
        return self._state

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast_snapshot(self) -> None:
        if not self._connections:
            return
        payload = json.dumps(self._state.model_dump(), default=str)
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


hub = LiveEnergyHub()
