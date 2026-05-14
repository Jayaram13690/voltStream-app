import { Card } from "../../../components/ui/Card.jsx";

export function BillingSummary({ summary }) {
  const pct = summary.budget_limit > 0 ? Math.min(100, Math.round((summary.predicted_bill / summary.budget_limit) * 100)) : 0;
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <Card>
        <div className="text-xs text-vs-muted">Current bill</div>
        <div className="mt-2 text-3xl font-semibold">${summary.current_bill.toFixed(2)}</div>
      </Card>
      <Card>
        <div className="text-xs text-vs-muted">Predicted bill</div>
        <div className="mt-2 text-3xl font-semibold">${summary.predicted_bill.toFixed(2)}</div>
        <div className="mt-2 text-xs text-vs-muted">{pct}% of monthly budget</div>
      </Card>
      <Card>
        <div className="text-xs text-vs-muted">Budget limit</div>
        <div className="mt-2 text-3xl font-semibold">${summary.budget_limit.toFixed(2)}</div>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-vs-primary" style={{ width: `${pct}%` }} />
        </div>
      </Card>
    </div>
  );
}
