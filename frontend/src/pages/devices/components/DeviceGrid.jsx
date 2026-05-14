import { DeviceCard } from "./DeviceCard.jsx";

export function DeviceGrid({ devices, busyId, onToggle }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {devices.map((d) => (
        <DeviceCard key={d.id} device={d} busy={busyId === d.id} onToggle={onToggle} />
      ))}
    </div>
  );
}
