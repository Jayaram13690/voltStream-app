import { useState, useEffect, useRef } from "react";
import { MessageCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useChatStore } from "../../store/chatStore";
import { ChatHeader } from "./ChatHeader";
import { ChatMessageList } from "./ChatMessageList";
import { ChatInputArea } from "./ChatInputArea";
import { MinimizedChat } from "./MinimizedChat";
import { ModeChangeNotification } from "./ModeChangeNotification";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeTab, setActiveTab] = useState("chat"); // 'chat' or 'rag'
  const [mode, setMode] = useState("normal"); // 'normal' or 'agent'
  const [modeNotification, setModeNotification] = useState(null); // Mode change notification
  const { 
    chatMessages, 
    ragMessages, 
    isLoading, 
    error, 
    sendMessage,
    clearChat,
    clearRag
  } = useChatStore();
  
  const messages = activeTab === "chat" ? chatMessages : ragMessages;
  const chatContainerRef = useRef(null);
  
  // Safety check for messages
  const safeMessages = Array.isArray(messages) ? messages : [];
  
  // Auto-scroll to bottom
  useEffect(() => {
    if (isOpen && !isMinimized && chatContainerRef.current) {
      // Use requestAnimationFrame for smoother scrolling
      const scrollToBottom = () => {
        requestAnimationFrame(() => {
          chatContainerRef.current.scrollTo({ 
            top: chatContainerRef.current.scrollHeight, 
            behavior: 'instant' 
          });
        });
      };
      
      // Small delay to allow animations to start
      const timer = setTimeout(scrollToBottom, 50);
      
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
      try {
        sendMessage(question, activeTab, mode);
      } catch (error) {
        console.error('Error sending message:', error);
        // Set error state if needed
      }
    }
  };

  const handleModeChange = (newMode) => {
    try {
      console.log('Changing mode to:', newMode);
      // Clear any existing notification first
      setModeNotification(null);
      setMode(newMode);
      setModeNotification(newMode);
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        console.log('Dismissing mode notification');
        setModeNotification(null);
      }, 5000);
    } catch (error) {
      console.error('Error in handleModeChange:', error);
    }
  };
  
  const handleResetChat = () => {
    if (activeTab === 'chat') {
      clearChat();
    } else {
      clearRag();
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
            <div className="w-[400px] md:w-[500px] lg:w-[600px] h-[600px] md:h-[650px] lg:h-[700px] bg-vs-card rounded-2xl shadow-2xl border border-vs-border overflow-hidden flex flex-col">
              <ChatHeader 
                onMinimize={minimizeChat} 
                onClose={toggleChat} 
                activeTab={activeTab}
                onReset={handleResetChat}
              />
              <div className="px-4 py-2 bg-vs-primary/5 border-b border-vs-border">
                <div className="flex p-1 bg-vs-primary/10 rounded-lg">
                  <motion.button
                    onClick={() => setActiveTab("chat")}
                    className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none ${
                      activeTab === "chat"
                        ? "bg-vs-primary text-white shadow-sm"
                        : "bg-transparent text-vs-text hover:bg-vs-primary/10"
                    }`}
                    whileHover={{ scale: 1.02, transition: { type: "spring", stiffness: 300, damping: 30 } }}
                    whileTap={{ scale: 0.98, transition: { type: "spring", stiffness: 300, damping: 25 } }}
                  >
                    AI Chat
                  </motion.button>
                  <motion.button
                    onClick={() => setActiveTab("rag")}
                    className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors focus:outline-none ${
                      activeTab === "rag"
                        ? "bg-vs-primary text-white shadow-sm"
                        : "bg-transparent text-vs-text hover:bg-vs-primary/10"
                    }`}
                    whileHover={{ scale: 1.02, transition: { type: "spring", stiffness: 300, damping: 30 } }}
                    whileTap={{ scale: 0.98, transition: { type: "spring", stiffness: 300, damping: 25 } }}
                  >
                    RAG Assistant
                  </motion.button>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto" ref={chatContainerRef}>
                {modeNotification && (
                  <AnimatePresence>
                    <motion.div
                      key="mode-notification"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      <ModeChangeNotification 
                        mode={modeNotification}
                        onDismiss={() => setModeNotification(null)}
                      />
                    </motion.div>
                  </AnimatePresence>
                )}
                <ChatMessageList 
                  messages={safeMessages} 
                  isLoading={isLoading} 
                  error={error}
                  activeTab={activeTab}
                  mode={mode}
                />
              </div>
              <ChatInputArea 
                onSubmit={handleSubmit} 
                isLoading={isLoading}
                activeTab={activeTab}
                mode={mode}
                onModeChange={handleModeChange}
              />
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}