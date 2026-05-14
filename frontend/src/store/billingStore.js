import { create } from "zustand";

export const useBillingStore = create((set) => ({
  summary: null,
  loading: false,
  error: null,
  setSummary: (summary) => set({ summary }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
