import clsx from "clsx";

const options = [
  { id: "daily", label: "Daily" },
  { id: "weekly", label: "Weekly" },
  { id: "monthly", label: "Monthly" },
];

export function PeriodSelector({ value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={o.id}
          type="button"
          onClick={() => onChange(o.id)}
          className={clsx(
            "rounded-xl border px-4 py-2 text-sm transition",
            value === o.id
              ? "border-vs-primary/40 bg-vs-primary/15 text-white"
              : "border-white/10 bg-white/5 text-vs-muted hover:bg-white/10",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
