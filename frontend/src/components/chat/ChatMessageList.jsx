import { motion, AnimatePresence } from "framer-motion";
import { ChatMessage } from "./ChatMessage";
import { forwardRef } from "react";

export const ChatMessageList = forwardRef(({ messages, isLoading, error, scrollContainerRef }, ref) => {
  return (
    <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-3 space-y-2">
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.timestamp}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{
              delay: index * 0.05, 
              duration: 0.4,
              ease: [0.4, 0, 0.2, 1]
            }}
          >
            <ChatMessage 
              role={message.role} 
              content={message.content} 
              timestamp={message.timestamp} 
              compact={true}
            />
          </motion.div>
        ))}
      </AnimatePresence>
      {isLoading && (
        <div className="flex items-center gap-2 text-vs-muted">
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
        </div>
      )}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
          className="text-vs-danger text-center py-2 text-sm"
        >
          {error}
        </motion.div>
      )}
    </div>
  );
});