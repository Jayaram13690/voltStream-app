import clsx from "clsx";

export function Modal({ open, title, children, onClose, className }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className={clsx("glass w-full max-w-lg rounded-2xl p-5", className)}>
        <div className="mb-3 flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button
            type="button"
            className="rounded-lg px-2 py-1 text-sm text-vs-muted hover:bg-white/10"
            onClick={onClose}
          >
            Close
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
