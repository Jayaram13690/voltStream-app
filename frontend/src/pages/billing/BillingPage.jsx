import { useEffect, useState } from "react";
import { toast } from "sonner";
import { PieChart } from "../../components/charts/PieChart.jsx";
import { Header } from "../../components/layout/Header.jsx";
import { Card } from "../../components/ui/Card.jsx";
import { Spinner } from "../../components/ui/Spinner.jsx";
import { api } from "../../services/api.js";
import { useBillingStore } from "../../store/billingStore.js";
import { BillingChart } from "./components/BillingChart.jsx";
import { BillingSummary } from "./components/BillingSummary.jsx";
import { TransactionTable } from "./components/TransactionTable.jsx";

export function BillingPage() {
  const summary = useBillingStore((s) => s.summary);
  const setSummary = useBillingStore((s) => s.setSummary);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await api.get("/api/v1/billing/summary");
        if (!cancelled) setSummary(res.data);
      } catch {
        toast.error("Could not load billing.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [setSummary]);

  if (loading || !summary) {
    return (
      <div className="flex min-h-[40vh] items-center gap-2 text-vs-muted">
        <Spinner className="h-6 w-6" />
        Loading billing…
      </div>
    );
  }

  const headroom = Math.max(0, summary.budget_limit - summary.predicted_bill);
  const pieData = [
    { name: "Current", value: summary.current_bill },
    { name: "Predicted delta", value: Math.max(0, summary.predicted_bill - summary.current_bill) },
    { name: "Budget headroom", value: headroom },
  ];

  return (
    <div>
      <Header title="Billing" subtitle="Budget guardrails, projections, and payment history." />
      <BillingSummary summary={summary} />
      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <div className="mb-2 text-sm font-semibold">Bill outlook</div>
          <BillingChart />
        </Card>
        <Card>
          <div className="mb-2 text-sm font-semibold">Cost composition</div>
          <PieChart data={pieData} nameKey="name" valueKey="value" colors={["#3b82f6", "#f59e0b", "#10b981"]} height={280} />
        </Card>
      </div>
      <div className="mt-4">
        <Card>
          <div className="mb-3 text-sm font-semibold">Payment history</div>
          <TransactionTable rows={summary.transactions} />
        </Card>
      </div>
    </div>
  );
}
