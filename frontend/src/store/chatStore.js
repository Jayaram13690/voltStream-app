import { create } from 'zustand'
import { api } from '../services/api'

// Initialize with welcome message only once
const initialChatMessages = []
const initialRagMessages = []

// Check if we need to add welcome message (only on first load)
if (initialChatMessages.length === 0) {
  initialChatMessages.push({
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

if (initialRagMessages.length === 0) {
  initialRagMessages.push({
    role: 'ai',
    content: "Hello! I'm your Document Assistant.\n" +
              "I can answer questions from the indexed solar energy documents.\n" +
              "Ask me about specific solar energy topics, technologies, or concepts.",
    timestamp: new Date()
  })
}

export const useChatStore = create((set, get) => ({
  chatMessages: initialChatMessages,
  ragMessages: initialRagMessages,
  isLoading: false,
  error: null,
  
  addChatMessage: (role, content) => set(state => ({
    chatMessages: [...state.chatMessages, { role, content, timestamp: new Date() }]
  })),
  
  addRagMessage: (role, content, context = null) => set(state => ({
    ragMessages: [...state.ragMessages, { role, content, timestamp: new Date(), context }]
  })),
  
  sendMessage: async (question, mode = 'chat') => {
    set({ isLoading: true, error: null })
    
    if (mode === 'chat') {
      get().addChatMessage('user', question)
    } else {
      get().addRagMessage('user', question)
    }
    
    try {
      let response
      if (mode === 'chat') {
        response = await api.post('/api/v1/chat', { question })
        get().addChatMessage('ai', response.data.answer)
      } else {
        response = await api.post('/api/v1/qa', { question })
        get().addRagMessage('ai', response.data.answer, response.data.context_used || null)
      }
    } catch (error) {
      set({ error: error.message })
    } finally {
      set({ isLoading: false })
    }
  },
  
  clearChat: () => set({ chatMessages: [] }),
  clearRag: () => set({ ragMessages: [] })
}))