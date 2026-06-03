import { motion } from "framer-motion";
import { X } from "lucide-react";

export function MinimizedChat({ onRestore, onClose }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="fixed bottom-6 right-6 z-50 w-80 bg-vs-primary text-white p-3 rounded-2xl shadow-2xl border border-vs-border flex items-center justify-between cursor-pointer"
      onClick={onRestore}
    >
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ rotate: [0, 5, -5, 5, 0] }}
          transition={{ repeat: Infinity, duration: 4 }}
          className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center"
        >
          🤖
        </motion.div>
        <div className="font-medium text-sm">VoltStream AI Assistant</div>
      </div>
      <button 
        whileHover={{ scale: 1.2, rotate: -10 }}
        whileTap={{ scale: 0.8, opacity: 0.9, rotate: 0 }}
        transition={{ type: "spring", stiffness: 600, damping: 20 }}
        onClick={(e) => {e.stopPropagation(); onClose();}}
        className="p-1 rounded hover:bg-white/20 transition-colors"
        aria-label="Close chat"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
}