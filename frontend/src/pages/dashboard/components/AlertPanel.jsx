import { AlertTriangle, Info } from "lucide-react";
import { Card } from "../../../components/ui/Card.jsx";
import clsx from "clsx";

export function AlertPanel({ alerts }) {
  return (
    <Card>
      <div className="mb-3 text-sm font-semibold">Active alerts</div>
      <div className="space-y-2">
        {alerts.map((a) => (
          <div
            key={a.id}
            className={clsx(
              "flex items-start gap-3 rounded-xl border px-3 py-2 text-sm",
              a.level === "warning"
                ? "border-vs-warning/30 bg-vs-warning/10 text-vs-text"
                : "border-white/10 bg-white/5 text-vs-text",
            )}
          >
            {a.level === "warning" ? (
              <AlertTriangle className="mt-0.5 h-4 w-4 text-vs-warning" />
            ) : (
              <Info className="mt-0.5 h-4 w-4 text-vs-primary" />
            )}
            <div>{a.message}</div>
          </div>
        ))}
      </div>
    </Card>
  );
}
