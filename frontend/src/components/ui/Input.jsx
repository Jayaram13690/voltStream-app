import clsx from "clsx";

export function Input({ className, ...props }) {
  return (
    <input
      className={clsx(
        "w-full rounded-xl border border-white/10 bg-vs-card px-3 py-2 text-sm text-vs-text outline-none ring-vs-primary/40 focus:ring-2",
        className,
      )}
      {...props}
    />
  );
}
