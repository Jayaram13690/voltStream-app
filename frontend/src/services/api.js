import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL?.trim() || "";

export const api = axios.create({
  baseURL,
  timeout: 15000,
});

export function wsLiveEnergyUrl() {
  const configured = import.meta.env.VITE_API_URL?.trim();
  if (configured) {
    const u = new URL("/ws/live-energy", configured);
    u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
    return u.toString();
  }
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/live-energy`;
}
