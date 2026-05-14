import { Card } from "../../../components/ui/Card.jsx";
import { ToggleSwitch } from "./ToggleSwitch.jsx";

export function DeviceCard({ device, busy, onToggle }) {
  const on = device.status === "on";
  return (
    <Card className="hover:-translate-y-0.5 transition-transform">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold">{device.name}</div>
          <div className="mt-1 text-xs text-vs-muted">{on ? "Drawing power" : "Idle"}</div>
        </div>
        <ToggleSwitch checked={on} disabled={busy} onChange={() => onToggle(device, !on)} />
      </div>
      <div className="mt-4 flex items-end justify-between">
        <div>
          <div className="text-xs text-vs-muted">Power</div>
          <div className="text-xl font-semibold">{device.power_usage?.toFixed?.(1) ?? device.power_usage} kW</div>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-1 text-[11px] text-vs-muted">#{device.id}</div>
      </div>
    </Card>
  );
}
