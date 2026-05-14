import { useEffect } from "react";
import { AppProviders } from "./app/AppProviders.jsx";
import { AppRoutes } from "./routes/AppRoutes.jsx";
import { useAuthStore } from "./store/authStore.js";

export default function App() {
  const theme = useAuthStore((s) => s.theme);

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.add("light");
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  return (
    <AppProviders>
      <AppRoutes />
    </AppProviders>
  );
}
