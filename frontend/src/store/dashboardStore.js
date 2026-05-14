import { create } from "zustand";

export const useDashboardStore = create((set) => ({
  live: null,
  alerts: [
    { id: 1, level: "warning", message: "Peak window starts in 45 minutes" },
    { id: 2, level: "info", message: "Solar forecast: strong afternoon production" },
  ],
  setLive: (live) => set({ live }),
}));
