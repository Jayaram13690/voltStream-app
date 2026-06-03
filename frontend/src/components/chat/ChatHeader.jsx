import { motion } from "framer-motion";
import { X, Minimize2 } from "lucide-react";

export function ChatHeader({ onMinimize, onClose, activeTab = "chat" }) {
  return (
    <div className="bg-vs-primary text-white p-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ repeat: Infinity, duration: 8, ease: "easeInOut" }}
          className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center"
        >
          🤖
        </motion.div>
        <div>
          <div className="font-semibold text-sm">
            {activeTab === "chat" ? "AI Assistant" : "Document Assistant"}
          </div>
          <div className="text-xs opacity-80">
            {activeTab === "chat" ? "Ask general energy-related questions" : "Ask questions from indexed solar energy documents"}
          </div>
        </div>
      </div>
      <div className="flex gap-2">
        <motion.button
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.85, opacity: 0.9, rotate: 0 }}
          transition={{ type: "spring", stiffness: 600, damping: 20 }}
          onClick={onMinimize}
          className="p-1 rounded hover:bg-white/20 transition-colors"
          aria-label="Minimize chat"
        >
          <Minimize2 className="w-4 h-4" />
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.1, rotate: -5 }}
          whileTap={{ scale: 0.85, opacity: 0.9, rotate: 0 }}
          transition={{ type: "spring", stiffness: 600, damping: 20 }}
          onClick={onClose}
          className="p-1 rounded hover:bg-white/20 transition-colors"
          aria-label="Close chat"
        >
          <X className="w-4 h-4" />
        </motion.button>
      </div>
    </div>
  );
}