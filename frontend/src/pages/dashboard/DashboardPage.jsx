import { useEffect } from "react";
import { toast } from "sonner";
import { Header } from "../../components/layout/Header.jsx";
import { Card } from "../../components/ui/Card.jsx";
import { Spinner } from "../../components/ui/Spinner.jsx";
import { api } from "../../services/api.js";
import { useDashboardStore } from "../../store/dashboardStore.js";
import { useDeviceStore } from "../../store/deviceStore.js";
import { useLiveEnergyPolling } from "../../hooks/useLiveEnergyPolling.js";
import { DeviceStatus } from "./components/DeviceStatus.jsx";
import { EnergyCard } from "./components/EnergyCard.jsx";
import { UsageChart } from "./components/UsageChart.jsx";

export function DashboardPage() {
  const live = useDashboardStore((s) => s.live);
  const alerts = useDashboardStore((s) => s.alerts);
  const setLive = useDashboardStore((s) => s.setLive);
  const devices = useDeviceStore((s) => s.devices);
  const setDevices = useDeviceStore((s) => s.setDevices);

  useLiveEnergyPolling();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [dash, devs] = await Promise.all([
          api.get("/api/v1/dashboard/live"),
          api.get("/api/v1/devices"),
        ]);
        if (cancelled) return;
        // Handle new polling data structure
        const dashData = dash.data.data || dash.data;
        setLive(dashData);
        setDevices(devs.data);
      } catch {
        toast.error("Could not load dashboard data. Is the API running?");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [setDevices, setLive]);

  if (!live) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center gap-3 text-vs-muted">
        <Spinner />
        Connecting to VoltStream…
      </div>
    );
  }

  return (
    <div>
      <Header title="Dashboard" subtitle="Live energy flow, savings, and device posture." />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <EnergyCard title="Grid usage" value={`${Number(live.grid_usage).toFixed(2)} kW`} hint="Net import from utility" accent="primary" />
        <EnergyCard title="Solar generation" value={`${Number(live.solar_generation).toFixed(2)} kW`} hint="Array output (simulated)" accent="success" />
        <EnergyCard title="Battery" value={`${Number(live.battery).toFixed(0)}%`} hint="State of charge" accent="warning" />
        <EnergyCard title="MTD savings" value={`$${live.savings.toFixed(0)}`} hint="Vs. baseline tariff" accent="success" />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold">Consumption vs solar</div>
              <div className="text-xs text-vs-muted">Area chart with live endpoints blended into a rolling window</div>
            </div>
          </div>
          <UsageChart gridUsage={live.grid_usage} solarGeneration={live.solar_generation} />
        </Card>
        <div className="space-y-4">
          <DeviceStatus devices={devices} />
        </div>
      </div>
    </div>
  );
}
