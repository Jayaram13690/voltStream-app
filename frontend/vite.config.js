import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://backend:8000", changeOrigin: true },
      "/ws": { target: "ws://backend:8000", ws: true },
      "/health": { target: "http://backend:8000", changeOrigin: true },
    },
  },
});
