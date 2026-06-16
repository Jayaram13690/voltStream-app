"""
General AI Chat Service - handles non-document conversations.
Completely separate from RAG service.
"""

from app.services.simple_chat_memory import get_simple_chat_memory
from app.services.bedrock_service import get_bedrock_service


class ChatService:
    """
    Service for general AI chat with conversation continuity.
    Does NOT use document retrieval - pure LLM conversation.
    """
    
    def __init__(self):
        """Initialize chat service with conversation memory."""
        # Conversation history for general chat (10 messages = 5 Q&A pairs)
        self.chat_memory = get_simple_chat_memory(max_history=10)
        self.bedrock_service = get_bedrock_service()
    
    def chat(self, question: str) -> str:
        """Handle general AI chat with conversation history."""
        # Add user question to conversation history
        self.chat_memory.add_ai_message("user", question)
        
        # Get conversation context
        conversation_context = self.chat_memory.get_ai_context()
        
        # Generate response using Bedrock with conversation context
        prompt = f"""You are a helpful AI assistant. Use the conversation history below to understand context and provide accurate responses. You can answer general knowledge questions about any topic.

CONVERSATION HISTORY:
{conversation_context}

USER QUESTION: {question}

RESPONSE:"""
        
        response = self.bedrock_service.generate_response(prompt)
        
        # Add AI response to conversation history
        self.chat_memory.add_ai_message("ai", response)
        
        return response
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.chat_memory.clear_ai_history()