import json
import random
import time

from app.schemas.dashboard import DashboardLive


class LiveEnergyHub:
    def __init__(self) -> None:
        self._state = DashboardLive(
            grid_usage=4.2,
            solar_generation=6.8,
            battery=82,
            savings=2340.0,
        )
        self._last_updated = time.time()

    @property
    def state(self) -> DashboardLive:
        return self._state

    def tick(self) -> DashboardLive:
        g = max(0.0, self._state.grid_usage + random.uniform(-0.35, 0.35))
        s = max(0.0, self._state.solar_generation + random.uniform(-0.6, 0.6))
        b = int(max(0, min(100, self._state.battery + random.randint(-1, 1))))
        sv = max(0.0, self._state.savings + random.uniform(-5, 12))
        self._state = DashboardLive(grid_usage=round(g, 2), solar_generation=round(s, 2), battery=b, savings=round(sv, 2))
        self._last_updated = time.time()
        return self._state

    def generate_sse(self):
        while True:
            self.tick()
            payload = json.dumps(self._state.model_dump(), default=str)
            yield f"data: {payload}\n\n"
            time.sleep(2)

    def get_state(self, since: float = None, auto_tick: bool = True) -> dict:
        """Get current state with optional change detection for polling"""
        current_time = time.time()
        
        # Auto-tick if enabled (for polling mode)
        if auto_tick:
            self.tick()
        
        if since is not None and self._last_updated <= since:
            return {"changed": False, "timestamp": current_time}
        
        return {
            "changed": True,
            "timestamp": current_time,
            "data": self._state.model_dump()
        }


hub = LiveEnergyHub()