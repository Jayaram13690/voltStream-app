import { useState, useEffect, useRef } from "react";
import { MessageCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useChatStore } from "../../store/chatStore";
import { ChatHeader } from "./ChatHeader";
import { ChatMessageList } from "./ChatMessageList";
import { ChatInputArea } from "./ChatInputArea";
import { MinimizedChat } from "./MinimizedChat";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const { messages, isLoading, error, sendMessage } = useChatStore();
  const chatContainerRef = useRef(null);
  
  // Auto-scroll to bottom
  useEffect(() => {
    if (isOpen && !isMinimized && chatContainerRef.current) {
      // Use setTimeout to ensure DOM is updated before scrolling
      const timer = setTimeout(() => {
        chatContainerRef.current.scrollTo({ 
          top: chatContainerRef.current.scrollHeight, 
          behavior: 'smooth' 
        });
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [messages, isOpen, isMinimized]);
  
  const toggleChat = () => {
    setIsOpen(!isOpen);
    setIsMinimized(false);
  };
  
  const minimizeChat = () => {
    setIsMinimized(true);
  };
  
  const restoreChat = () => {
    setIsMinimized(false);
  };
  
  const handleSubmit = (e, question) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      sendMessage(question);
    }
  };
  
  // Animation variants with enhanced smoothness
  const chatVariants = {
    hidden: { opacity: 0, scale: 0.85, y: 40 },
    visible: {
      opacity: 1, 
      scale: 1, 
      y: 0,
      transition: {
        duration: 0.5,
        ease: [0.4, 0, 0.2, 1]
      }
    },
    exit: {
      opacity: 0, 
      scale: 0.9,
      y: 30,
      transition: {
        duration: 0.4,
        ease: [0.4, 0, 0.2, 1]
      }
    }
  };

  const minimizedVariants = {
    hidden: { 
      opacity: 0, 
      y: 30,
      scale: 0.9,
      transition: { duration: 0.3 }
    },
    visible: {
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        duration: 0.4,
        ease: [0.4, 0, 0.2, 1]
      }
    },
    exit: {
      opacity: 0, 
      y: -30,
      scale: 0.95,
      transition: {
        duration: 0.3,
        ease: [0.4, 0, 0.2, 1]
      }
    }
  };

  return (
    <AnimatePresence>
      {!isOpen ? (
        <motion.button
          whileTap={{ scale: 0.9, opacity: 0.9 }}
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 600, damping: 20 }}
          onClick={toggleChat}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-vs-primary rounded-full shadow-lg hover:bg-vs-primary/90 transition-all duration-200 flex items-center justify-center text-white"
          aria-label="Open AI Assistant"
        >
          <MessageCircle className="w-7 h-7" />
        </motion.button>
      ) : (
        <motion.div
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={isMinimized ? minimizedVariants : chatVariants}
          transition={{ 
            type: "spring",
            stiffness: 500,
            damping: 25,
            mass: 0.8
          }}
          className="fixed bottom-6 right-6 z-50"
        >
          {isMinimized ? (
            <MinimizedChat onRestore={restoreChat} onClose={toggleChat} />
          ) : (
            <div className="w-[400px] bg-vs-card rounded-2xl shadow-2xl border border-vs-border overflow-hidden max-h-[600px] flex flex-col">
              <ChatHeader onMinimize={minimizeChat} onClose={toggleChat} />
              <ChatMessageList 
                messages={messages} 
                isLoading={isLoading} 
                error={error}
                scrollContainerRef={chatContainerRef}
              />
              <ChatInputArea 
                onSubmit={handleSubmit} 
                isLoading={isLoading}
              />
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}