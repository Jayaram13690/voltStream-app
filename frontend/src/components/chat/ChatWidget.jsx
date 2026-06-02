import { useState, useEffect, useRef } from "react"
import { MessageCircle, X, Minimize2 } from "lucide-react"
import { useChatStore } from "../../store/chatStore"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const { messages, isLoading, error, sendMessage } = useChatStore()
  const chatContainerRef = useRef(null)
  
  // Auto-scroll to bottom
  useEffect(() => {
    if (isOpen && !isMinimized) {
      chatContainerRef.current?.scrollTo({ 
        top: chatContainerRef.current.scrollHeight, 
        behavior: 'smooth' 
      })
    }
  }, [messages, isOpen, isMinimized])
  
  const toggleChat = () => {
    if (isMinimized) {
      setIsMinimized(false)
    } else {
      setIsOpen(!isOpen)
    }
  }
  
  const minimizeChat = () => {
    setIsMinimized(true)
  }
  
  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen ? (
        <button 
          onClick={toggleChat}
          className="w-14 h-14 bg-vs-primary rounded-full shadow-lg hover:bg-vs-primary/90 transition-all duration-300 flex items-center justify-center text-white"
          aria-label="Open AI Assistant"
        >
          <MessageCircle className="w-7 h-7" />
        </button>
      ) : (
        <div className="w-[400px] bg-vs-card rounded-2xl shadow-2xl border border-vs-border overflow-hidden max-h-[600px] flex flex-col">
          {/* Chat Header */}
          <div className="bg-vs-primary text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                🤖
              </div>
              <div>
                <div className="font-semibold text-sm">VoltStream AI Assistant</div>
                <div className="text-xs opacity-80">Ask me anything</div>
              </div>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={minimizeChat}
                className="p-1 rounded hover:bg-white/20 transition-colors"
                aria-label="Minimize chat"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button 
                onClick={toggleChat}
                className="p-1 rounded hover:bg-white/20 transition-colors"
                aria-label="Close chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {/* Chat Messages */}
          <div 
            ref={chatContainerRef} 
            className="flex-1 overflow-y-auto p-3 space-y-2"
          >
            {messages.map((message, index) => (
              <ChatMessage 
                key={index} 
                role={message.role} 
                content={message.content} 
                timestamp={message.timestamp} 
                compact={true}
              />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-vs-muted">
                <span className="w-2 h-2 bg-vs-primary rounded-full animate-pulse"></span>
                <span className="w-2 h-2 bg-vs-primary rounded-full animate-pulse delay-100"></span>
                <span className="w-2 h-2 bg-vs-primary rounded-full animate-pulse delay-200"></span>
              </div>
            )}
            {error && (
              <div className="text-vs-danger text-center py-2 text-sm">{error}</div>
            )}
          </div>
          
          {/* Chat Input */}
          <div className="p-3 border-t border-vs-border bg-vs-bg">
            <ChatInput 
              onSubmit={(e, question) => {
                e.preventDefault()
                if (question.trim() && !isLoading) {
                  sendMessage(question)
                }
              }}
              isLoading={isLoading}
              compact={true}
            />
          </div>
        </div>
      )}
    </div>
  )
}