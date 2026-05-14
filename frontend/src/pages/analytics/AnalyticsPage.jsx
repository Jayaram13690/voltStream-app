import { useEffect } from "react";
import { toast } from "sonner";
import { BarChart } from "../../components/charts/BarChart.jsx";
import { Header } from "../../components/layout/Header.jsx";
import { Card } from "../../components/ui/Card.jsx";
import { Spinner } from "../../components/ui/Spinner.jsx";
import { api } from "../../services/api.js";
import { useAnalyticsStore } from "../../store/analyticsStore.js";
import { ConsumptionChart } from "./components/ConsumptionChart.jsx";
import { PeriodSelector } from "./components/PeriodSelector.jsx";
import { StatsCards } from "./components/StatsCards.jsx";

export function AnalyticsPage() {
  const period = useAnalyticsStore((s) => s.period);
  const setPeriod = useAnalyticsStore((s) => s.setPeriod);
  const history = useAnalyticsStore((s) => s.history);
  const setHistory = useAnalyticsStore((s) => s.setHistory);
  const loading = useAnalyticsStore((s) => s.loading);
  const setLoading = useAnalyticsStore((s) => s.setLoading);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await api.get("/api/v1/analytics/history", { params: { period } });
        if (!cancelled) setHistory(res.data);
      } catch {
        toast.error("Could not load analytics.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [period, setHistory, setLoading]);

  const points = history?.points ?? [];

  return (
    <div>
      <Header title="Analytics" subtitle="Usage by period with quick trend readouts." />
      <PeriodSelector value={period} onChange={setPeriod} />
      <StatsCards points={points} />
      {loading && !history ? (
        <div className="mt-6 flex items-center gap-2 text-vs-muted">
          <Spinner className="h-6 w-6" />
          Loading analytics…
        </div>
      ) : (
        <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
          <Card>
            <div className="mb-2 text-sm font-semibold">Consumption vs solar</div>
            <ConsumptionChart points={points} />
          </Card>
          <Card>
            <div className="mb-2 text-sm font-semibold">Net energy mix</div>
            <BarChart
              data={points.map((p) => ({ label: p.label, net: Math.max(0, p.consumption - p.solar) }))}
              xKey="label"
              bars={[{ dataKey: "net", name: "Net draw (kWh proxy)", color: "#ff3366" }]}
              height={300}
            />
          </Card>
        </div>
      )}
    </div>
  );
}
