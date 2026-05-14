import { Route, Routes } from "react-router-dom";
import { MainLayout } from "../layouts/MainLayout.jsx";
import { AnalyticsPage } from "../pages/analytics/AnalyticsPage.jsx";
import { BillingPage } from "../pages/billing/BillingPage.jsx";
import { DashboardPage } from "../pages/dashboard/DashboardPage.jsx";
import { DevicesPage } from "../pages/devices/DevicesPage.jsx";
import { SettingsPage } from "../pages/settings/SettingsPage.jsx";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/devices" element={<DevicesPage />} />
        <Route path="/billing" element={<BillingPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
