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
  
  addChatMessage: (role, content, mode = 'normal', type = 'normal', sessionId = null, requestId = null) => set(state => ({
    chatMessages: [...state.chatMessages, { role, content, timestamp: new Date(), mode, type, sessionId, requestId }]
  })),
  
  addRagMessage: (role, content, mode = 'normal', type = 'normal', sessionId = null, requestId = null) => set(state => ({
    ragMessages: [...state.ragMessages, { role, content, timestamp: new Date(), mode, type, sessionId, requestId }]
  })),
  
  sendMessage: async (question, tab = 'chat', mode = 'normal') => {
    set({ isLoading: true, error: null })
    
    // Add user message to appropriate tab
    if (tab === 'chat') {
      get().addChatMessage('user', question, mode)
    } else {
      get().addRagMessage('user', question, mode)
    }
    
    try {
      let response
      let endpoint, requestBody
      
      // Determine endpoint and request format based on tab first, then mode
      if (tab === 'rag') {
        // RAG endpoint - always use RAG regardless of mode
        endpoint = '/api/v1/qa'
        requestBody = { question: question }  // RAG expects {question: "..."}
      } else if (mode === 'agent') {
        // Device Control Agent endpoint
        endpoint = '/api/v1/agent'
        requestBody = { message: question }  // Agent expects {message: "..."}
      } else if (mode === 'energy') {
        // Energy Advisor Agent endpoint
        endpoint = '/api/v1/energy-advisor'
        requestBody = { message: question }  // Energy advisor expects {message: "..."}
      } else if (mode === 'multi') {
        // Multi-Agent endpoint
        endpoint = '/api/v1/multi-agent'
        requestBody = { query: question }  // Multi-agent expects {query: "..."}
      } else {
        // General chat endpoint
        endpoint = '/api/v1/chat'
        requestBody = { question: question }  // Chat expects {question: "..."}
      }
      
      response = await api.post(endpoint, requestBody)
      
      // Debug: Log the actual response structure with mode info
      console.log(`[DEBUG] Mode: ${mode}, Endpoint: ${endpoint}, Response:`, response.data)
      
      // Add AI response to appropriate tab
      let answer
      if (tab === 'rag') {
        // RAG tab ALWAYS uses QA endpoint regardless of mode
        answer = response.data.answer || response.data.response || 'No answer received'
        
        // Debug: Check if we got a valid answer from QA
        if (!answer || answer === 'No answer received') {
          console.error('[QA ERROR] No valid answer found in response:', response.data)
        } else {
          console.log('[QA SUCCESS] Extracted answer:', answer)
        }
      } else if (mode === 'agent') {
        // Device agent in chat tab
        answer = response.data.response
      } else if (mode === 'energy') {
        // Energy advisor in chat tab
        answer = response.data.response
      } else if (mode === 'multi') {
        // Multi-agent response
        answer = response.data.response
        
        // Extract additional multi-agent fields
        const sessionId = response.data.session_id
        const requestId = response.data.request_id
        
        // Trigger device status update event for multi-agent changes
        // This ensures frontend gets notified of device changes made by multi-agent
        const deviceKeywords = ['turned on', 'turned off', 'updated', 'changed', 
                              'switched', 'toggled', 'set to', 'now on', 'now off',
                              'heat pump', 'ev charger', 'kitchen', 'hvac', 
                              'water heater', 'solar inverter', 'dishwasher', 'fan'];
        
        if (answer && deviceKeywords.some(keyword => answer.toLowerCase().includes(keyword))) {
          // Dispatch the same event that device agent triggers
          const event = new CustomEvent('deviceStatusUpdated', {
            detail: { 
              timestamp: new Date().toISOString(),
              source: 'multi_agent',
              answer: answer
            }
          });
          window.dispatchEvent(event);
          console.log('[MULTI-AGENT] Dispatched device update event for:', answer);
        }
        
        // Add AI response with multi-agent details
        if (tab === 'chat') {
          get().addChatMessage('ai', answer, mode, 'multi-agent', sessionId, requestId)
        } else {
          get().addRagMessage('ai', answer, mode, 'multi-agent', sessionId, requestId)
        }
        
        set({ isLoading: false })
        return
      } else {
        // Normal chat
        answer = response.data.answer || response.data.response || 'No answer received'
      }
      
      console.log(`[DEBUG] Extracted answer:`, answer)
      
      // Final safety check - ensure answer is a valid non-empty string
      if (!answer) {
        console.error('[CRITICAL] No answer found. Value:', answer)
        answer = 'Sorry, I could not process your request properly.'
      }
      
      if (tab === 'chat') {
        get().addChatMessage('ai', answer, mode)
      } else {
        get().addRagMessage('ai', answer, mode)
      }
      
      // If this was an agent operation, trigger a device data refresh
      if (mode === 'agent') {
        // Dispatch event to notify other components about device changes
        const event = new CustomEvent('deviceStatusUpdated', {
          detail: { 
            timestamp: new Date().toISOString(),
            source: 'device_agent'
          }
        })
        window.dispatchEvent(event)
        console.log('[DEVICE AGENT] Dispatched device update event');
      }
      
    } catch (error) {
      console.error('Chat error:', error)
      let errorMessage = 'Failed to get response from the server'
      let endpoint = null // Declare endpoint variable for error handling
      if (error.response) {
        // Server responded with a status code outside 2xx
        errorMessage = error.response.data.detail || 
                      error.response.data.message || 
                      error.response.data.error || 
                      errorMessage
        // Add endpoint info for debugging (endpoint may not be defined in all cases)
        if (endpoint) {
          console.error(`Endpoint: ${endpoint}, Status: ${error.response.status}`)
        }
        console.error('Response data:', error.response.data)
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Please check your connection.'
      } else {
        // Something happened in setting up the request
        errorMessage = error.message || errorMessage
      }
      set({ error: errorMessage })
    } finally {
      set({ isLoading: false })
    }
  },
  
  clearChat: () => set({ chatMessages: [] }),
  clearRag: () => set({ ragMessages: [] })
}))