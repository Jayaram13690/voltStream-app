export function Spinner({ className = "h-8 w-8" }) {
  return (
    <div
      className={`${className} animate-spin rounded-full border-2 border-white/20 border-t-vs-primary`}
      role="status"
      aria-label="Loading"
    />
  );
}
