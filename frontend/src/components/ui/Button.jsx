import clsx from "clsx";

export function Button({ className, variant = "primary", ...props }) {
  const variants = {
    primary: "bg-vs-primary text-white hover:brightness-110 shadow-sm",
    ghost: "border border-transparent bg-transparent text-vs-strong hover:bg-vs-border/50",
    outline: "border border-vs-border bg-transparent text-vs-strong hover:bg-vs-card shadow-sm"
  };

  const styles = variants[variant] || variants.primary;

  return (
    <button
      type="button"
      className={clsx(
        "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition-colors",
        styles,
        className,
      )}
      {...props}
    />
  );
}
