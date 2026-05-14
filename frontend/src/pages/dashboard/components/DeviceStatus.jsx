import { Card } from "../../../components/ui/Card.jsx";

export function DeviceStatus({ devices }) {
  const on = devices.filter((d) => d.status === "on").length;
  const off = devices.length - on;
  const load = devices.reduce((sum, d) => sum + (d.power_usage || 0), 0);
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm text-vs-muted">Devices</div>
          <div className="mt-1 text-2xl font-semibold">
            {on} on · {off} off
          </div>
          <div className="mt-2 text-xs text-vs-muted">Aggregate load {load.toFixed(1)} kW</div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-vs-muted">Live</div>
      </div>
    </Card>
  );
}
