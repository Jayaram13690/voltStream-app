import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL?.trim() || "";

export const api = axios.create({
  baseURL,
  timeout: 15000,
});

// export function sseLiveEnergyUrl() {
//   const configured = import.meta.env.VITE_API_URL?.trim();
//   if (configured) {
//     return new URL("/api/v1/dashboard/live-stream", configured).toString();
//   }
//   return `${window.location.origin}/api/v1/dashboard/live-stream`;
// }
