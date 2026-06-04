import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL?.trim() || "";

export const api = axios.create({
  baseURL,
  timeout: 30000, // Increased timeout for RAG operations
});

// Add request interceptor for better error handling
api.interceptors.request.use(
  (config) => {
    // Add any request headers or modifications here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle network errors and timeouts
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timeout. Please try again.'));
    } else if (error.code === 'ERR_NETWORK') {
      return Promise.reject(new Error('Network error. Please check your connection.'));
    } else if (error.response) {
      // Server responded with an error status code
      const errorMessage = error.response.data?.detail || 
                           error.response.data?.message || 
                           'Server error occurred';
      return Promise.reject(new Error(errorMessage));
    } else {
      // Something happened in setting up the request
      return Promise.reject(new Error('Failed to connect to the server'));
    }
  }
);

// export function sseLiveEnergyUrl() {
//   const configured = import.meta.env.VITE_API_URL?.trim();
//   if (configured) {
//     return new URL("/api/v1/dashboard/live-stream", configured).toString();
//   }
//   return `${window.location.origin}/api/v1/dashboard/live-stream`;
// }
