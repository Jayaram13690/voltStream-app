import { create } from "zustand";

export const useDeviceStore = create((set, get) => ({
  devices: [],
  loading: false,
  error: null,
  setDevices: (devices) => set({ devices }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  patchLocal: (id, partial) =>
    set({
      devices: get().devices.map((d) => (d.id === id ? { ...d, ...partial } : d)),
    }),
  

}));
