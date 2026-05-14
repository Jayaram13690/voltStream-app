import { create } from "zustand";

export const useAuthStore = create((set) => ({
  user: null,
  theme: "dark",
  setTheme: (theme) => set({ theme }),
}));
