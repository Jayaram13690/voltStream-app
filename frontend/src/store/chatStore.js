import { create } from 'zustand'
import { api } from '../services/api'

// Initialize with welcome message only once
const initialMessages = []

// Check if we need to add welcome message (only on first load)
if (initialMessages.length === 0) {
  initialMessages.push({
    role: 'ai',
    content: "Hello! I'm VoltStream AI Assistant.\n" +
              "Ask me anything about:\n" +
              "• Energy\n" +
              "• Solar Systems\n" +
              "• Sustainability\n" +
              "• Power Consumption\n" +
              "• Renewable Technologies",
    timestamp: new Date()
  })
}

export const useChatStore = create((set, get) => ({
  messages: initialMessages,
  isLoading: false,
  error: null,
  
  addMessage: (role, content) => set(state => ({
    messages: [...state.messages, { role, content, timestamp: new Date() }]
  })),
  
  sendMessage: async (question) => {
    set({ isLoading: true, error: null })
    get().addMessage('user', question)
    
    try {
      const response = await api.post('/api/v1/chat', { question })
      get().addMessage('ai', response.data.answer)
    } catch (error) {
      set({ error: error.message })
    } finally {
      set({ isLoading: false })
    }
  },
  
  clearChat: () => set({ messages: [] })
}))