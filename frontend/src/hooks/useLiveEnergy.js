import { useEffect, useRef } from "react";
import { wsLiveEnergyUrl } from "../services/api.js";
import { useDashboardStore } from "../store/dashboardStore.js";

export function useLiveEnergy() {
  const setLive = useDashboardStore((s) => s.setLive);
  const wsRef = useRef(null);

  useEffect(() => {
    const url = wsLiveEnergyUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        setLive(data);
      } catch {
        /* ignore */
      }
    };
    const ping = window.setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);
    return () => {
      window.clearInterval(ping);
      ws.close();
    };
  }, [setLive]);
}
