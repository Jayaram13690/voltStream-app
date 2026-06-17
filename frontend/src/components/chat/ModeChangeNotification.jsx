import { CheckCircle } from "lucide-react";

export function ModeChangeNotification({ mode, onDismiss }) {
  return (
    <div className="flex items-center gap-2 p-3 bg-vs-primary/5 rounded-lg mx-4 mb-2 border border-vs-primary/20">
      <CheckCircle className="w-4 h-4 text-vs-primary" />
      <span className="text-sm text-vs-primary font-medium">
        Mode changed: {mode === 'agent' ? 'Device Agent' : mode === 'energy' ? 'Energy Advisor' : 'Normal'}
      </span>
      <button
        onClick={onDismiss}
        className="ml-auto text-vs-muted hover:text-vs-primary transition-colors"
        onMouseDown={(e) => e.preventDefault()} // Prevent text selection
      >
        ×
      </button>
    </div>
  );
}