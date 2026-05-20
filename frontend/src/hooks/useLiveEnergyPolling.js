import { useEffect, useRef } from "react";
import { api } from "../services/api.js";
import { useDashboardStore } from "../store/dashboardStore.js";

export function useLiveEnergyPolling() {
  const setLive = useDashboardStore((s) => s.setLive);
  const pollIntervalRef = useRef(null);
  const lastTimestampRef = useRef(null);

  useEffect(() => {
    const fetchLiveData = async () => {
      try {
        const response = await api.get("/api/v1/dashboard/live", {
          params: {
            since: lastTimestampRef.current
          }
        });
        
        const data = response.data;
        
        if (data.changed && data.data) {
          setLive(data.data);
          lastTimestampRef.current = data.timestamp;
        } else if (!lastTimestampRef.current) {
          // Initial load - set the data even if not changed
          setLive(data.data || data);
          lastTimestampRef.current = data.timestamp;
        }
      } catch (error) {
        console.error("Polling failed:", error);
      }
    };

    // Initial fetch
    fetchLiveData();

    // Set up polling every 2 seconds
    pollIntervalRef.current = setInterval(fetchLiveData, 2000);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [setLive]);
}