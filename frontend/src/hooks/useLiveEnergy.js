import { useEffect, useRef } from "react";
import { sseLiveEnergyUrl } from "../services/api.js";
import { useDashboardStore } from "../store/dashboardStore.js";

export function useLiveEnergy() {
  const setLive = useDashboardStore((s) => s.setLive);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    const url = sseLiveEnergyUrl();
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;
    eventSource.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        setLive(data);
      } catch {
        /* ignore */
      }
    };
    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error);
      eventSource.close();
    };
    return () => {
      eventSource.close();
    };
  }, [setLive]);
}
