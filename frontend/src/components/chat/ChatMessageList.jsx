import { motion, AnimatePresence } from "framer-motion";
import { ChatMessage } from "./ChatMessage";
import { forwardRef } from "react";

export const ChatMessageList = forwardRef(({ messages, isLoading, error, activeTab = "chat", mode = "normal" }, ref) => {
  return (
    <div className="p-3 space-y-2">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.div
          key={`${activeTab}-messages`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
        >
          {messages.map((message, index) => (
          <motion.div
            key={message.timestamp || index}
            initial={{ opacity: 0, y: 15, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -15, scale: 0.95, position: "absolute", width: "100%" }}
            transition={{
              type: "spring",
              stiffness: 250,
              damping: 45,
              mass: 1.1,
              duration: 0.7
            }}
            layout
          >
            {message.role && message.content && (
              <ChatMessage 
                role={message.role} 
                content={message.content} 
                timestamp={message.timestamp}
                activeTab={activeTab}
                mode={message.mode || mode}
                compact={true}
              />
            )}
            {!message.role || !message.content ? (
              <div className="text-vs-muted text-sm py-2 px-3 rounded-lg bg-vs-muted/10">
                Invalid message format
              </div>
            ) : null}
          </motion.div>
        ))}
        </motion.div>
        {isLoading && (
        <motion.div
          key="loading"
          initial={{ opacity: 0, y: 10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 300, damping: 30, mass: 1.0 }}
          className="flex items-center gap-2 text-vs-muted"
        >
          <span className="text-sm">
            {activeTab === "chat" 
              ? (mode === "agent" ? "Controlling device" : mode === "energy" ? "Analyzing energy" : "Thinking")
              : "Searching documents"}
          </span>
          <motion.span
            className="w-2 h-2 bg-vs-primary rounded-full"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ repeat: Infinity, duration: 0.8, delay: 0 }}
          />
          <motion.span
            className="w-2 h-2 bg-vs-primary rounded-full"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ repeat: Infinity, duration: 0.8, delay: 0.2 }}
          />
          <motion.span
            className="w-2 h-2 bg-vs-primary rounded-full"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ repeat: Infinity, duration: 0.8, delay: 0.4 }}
          />
        </motion.div>
      )}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 30, mass: 1.0 }}
          className="text-vs-danger text-center py-2 text-sm bg-vs-danger/10 rounded-lg mx-2 my-1"
        >
          ⚠️ {error}
        </motion.div>
      )}
      </AnimatePresence>
    </div>
  );
});