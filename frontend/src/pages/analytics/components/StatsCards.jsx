import { Card } from "../../../components/ui/Card.jsx";

export function StatsCards({ points }) {
  const sum = (key) => points.reduce((acc, p) => acc + (p[key] || 0), 0);
  const consumption = sum("consumption");
  const solar = sum("solar");
  const ratio = consumption > 0 ? Math.round((solar / consumption) * 100) : 0;
  return (
    <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
      <Card>
        <div className="text-xs text-vs-muted">Total consumption (series)</div>
        <div className="mt-2 text-2xl font-semibold">{consumption.toFixed(1)}</div>
      </Card>
      <Card>
        <div className="text-xs text-vs-muted">Total solar (series)</div>
        <div className="mt-2 text-2xl font-semibold">{solar.toFixed(1)}</div>
      </Card>
      <Card>
        <div className="text-xs text-vs-muted">Self-generation index</div>
        <div className="mt-2 text-2xl font-semibold">{ratio}%</div>
        <div className="mt-1 text-xs text-vs-muted">Solar ÷ consumption</div>
      </Card>
    </div>
  );
}
