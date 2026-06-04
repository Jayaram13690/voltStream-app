import { motion, AnimatePresence } from "framer-motion";
import { ChatMessage } from "./ChatMessage";
import { forwardRef } from "react";

export const ChatMessageList = forwardRef(({ messages, isLoading, error, activeTab = "chat" }, ref) => {
  return (
    <div className="p-3 space-y-2">
      <AnimatePresence mode="wait">
        <motion.div
          key={`${activeTab}-messages`}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        >
          {messages.map((message, index) => (
            <motion.div
              key={message.timestamp || index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{
                delay: index * 0.05, 
                duration: 0.4,
                ease: [0.4, 0, 0.2, 1]
              }}
            >
              {message.role && message.content && (
                <ChatMessage 
                  role={message.role} 
                  content={message.content} 
                  timestamp={message.timestamp}
                  activeTab={activeTab}
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
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="flex items-center gap-2 text-vs-muted"
        >
          <span className="text-sm">
            {activeTab === "chat" ? "Thinking..." : "Searching documents..."}
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
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
          className="text-vs-danger text-center py-2 text-sm bg-vs-danger/10 rounded-lg mx-2 my-1"
        >
          ⚠️ {error}
        </motion.div>
      )}
      </AnimatePresence>
    </div>
  );
});