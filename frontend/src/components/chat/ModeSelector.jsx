import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { motion } from "framer-motion";

export function ModeSelector({ mode, onModeChange }) {
  const [isOpen, setIsOpen] = useState(false);
  
  // Debug log to verify component is rendering
  console.log('ModeSelector rendering with mode:', mode);

  const modes = [
    { value: "normal", label: "Normal", description: "General AI assistance" },
    { value: "agent", label: "Device Agent", description: "Control devices" },
    { value: "energy", label: "Energy Advisor", description: "Energy analysis & savings" }
  ];

  const currentMode = modes.find(m => m.value === mode) || modes[0];

  return (
    <div className="relative">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 bg-vs-primary/10 rounded-full text-sm font-medium hover:bg-vs-primary/20 transition-colors border border-vs-border min-w-[120px]"
        whileTap={{ scale: 0.95 }}
      >
        <span className="w-2 h-2 rounded-full" style={{
          backgroundColor: mode === 'agent' ? '#3b82f6' : mode === 'energy' ? '#f59e0b' : '#10b981'
        }}></span>
        <span>Mode: {currentMode.label}</span>
        <ChevronDown className="w-4 h-4" />
      </motion.button>

      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          className="absolute bottom-full left-0 mb-2 w-48 bg-vs-card rounded-lg shadow-lg border border-vs-border p-2 z-50"
        >
          {modes.map((m) => (
            <button
              key={m.value}
              onClick={() => {
                onModeChange(m.value);
                setIsOpen(false);
              }}
              className={`w-full text-left p-2 rounded-md text-sm flex items-center gap-2 hover:bg-vs-primary/10 transition-colors ${
                mode === m.value ? 'bg-vs-primary/10 font-medium' : ''
              }`}
            >
              <span className="w-2 h-2 rounded-full" style={{
                backgroundColor: m.value === 'agent' ? '#3b82f6' : m.value === 'energy' ? '#f59e0b' : '#10b981'
              }}></span>
              <div className="flex-1">
                <div>{m.label}</div>
                <div className="text-xs text-vs-text-muted">{m.description}</div>
              </div>
            </button>
          ))}
        </motion.div>
      )}
    </div>
  );
}