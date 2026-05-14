import clsx from "clsx";

export function ToggleSwitch({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={clsx(
        "relative h-7 w-12 rounded-full border transition",
        checked ? "border-vs-success/40 bg-vs-success/20" : "border-white/10 bg-white/5",
        disabled && "opacity-50",
      )}
      aria-pressed={checked}
    >
      <span
        className={clsx(
          "absolute top-0.5 h-6 w-6 rounded-full bg-white shadow transition",
          checked ? "left-6" : "left-0.5",
        )}
      />
    </button>
  );
}
