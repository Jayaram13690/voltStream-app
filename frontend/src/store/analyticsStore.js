import { create } from "zustand";

export const useAnalyticsStore = create((set) => ({
  period: "daily",
  history: null,
  loading: false,
  error: null,
  setPeriod: (period) => set({ period }),
  setHistory: (history) => set({ history }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
