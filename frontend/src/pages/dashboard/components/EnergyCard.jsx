import clsx from "clsx";

export function EnergyCard({ title, value, hint, accent = "primary" }) {
  const accentTextMap = {
    primary: "text-vs-primary",
    success: "text-vs-success",
    warning: "text-vs-warning",
    danger: "text-vs-danger",
  };
  
  const accentGlowMap = {
    primary: "shadow-[0_0_20px_rgba(255,51,102,0.15)]",
    success: "shadow-[0_0_20px_rgba(0,230,118,0.15)]",
    warning: "shadow-[0_0_20px_rgba(255,183,77,0.15)]",
    danger: "shadow-[0_0_20px_rgba(240,62,62,0.15)]",
  };

  return (
    <div
      className={clsx(
        "bento-card relative overflow-hidden p-6 flex flex-col justify-between",
        accentGlowMap[accent]
      )}
    >
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-vs-muted">{title}</div>
        <div className={clsx("h-2 w-2 rounded-full shadow-[0_0_8px_currentColor]", accentTextMap[accent])} />
      </div>
      <div className="mt-4">
        <div className="text-4xl font-bold tracking-tight text-vs-strong">{value}</div>
        {hint ? <div className={clsx("mt-2 text-xs font-medium", accentTextMap[accent])}>{hint}</div> : null}
      </div>
    </div>
  );
}
