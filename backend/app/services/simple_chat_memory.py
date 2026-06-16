"""
Simple chat memory service with completely isolated conversation histories.
AI chat and RAG chat maintain separate histories with no mixing.
"""

from typing import List, Dict


class SimpleChatMemory:
    """
    Simple chat memory service with isolated conversation histories.
    
    Attributes:
        ai_messages (List[Dict]): AI chat conversation history
        rag_messages (List[Dict]): RAG chat conversation history
        max_history (int): Maximum number of messages to keep per conversation
    """
    
    def __init__(self, max_history: int = 10):
        """Initialize with empty histories and max history limit."""
        self.ai_messages = []
        self.rag_messages = []
        self.max_history = max_history  # Keep last N messages
    
    def add_ai_message(self, role: str, content: str) -> None:
        """Add a message to AI conversation history."""
        self.ai_messages.append({
            "role": role,
            "content": content
        })
        
        # Trim to max history
        if len(self.ai_messages) > self.max_history:
            self.ai_messages = self.ai_messages[-self.max_history:]
    
    def add_rag_message(self, role: str, content: str) -> None:
        """Add a message to RAG conversation history."""
        self.rag_messages.append({
            "role": role,
            "content": content
        })
        
        # Trim to max history
        if len(self.rag_messages) > self.max_history:
            self.rag_messages = self.rag_messages[-self.max_history:]
    
    def get_ai_context(self) -> str:
        """Get formatted AI conversation context for LLM."""
        if not self.ai_messages:
            return ""
        
        context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.ai_messages
        ])
        
        return f"AI CONVERSATION HISTORY (last {len(self.ai_messages)} messages):\n{context}"
    
    def get_rag_context(self) -> str:
        """Get formatted RAG conversation context for LLM."""
        if not self.rag_messages:
            return ""
        
        context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.rag_messages
        ])
        
        return f"RAG CONVERSATION HISTORY (last {len(self.rag_messages)} messages):\n{context}"
    
    def clear_ai_history(self) -> None:
        """Clear AI conversation history."""
        self.ai_messages = []
    
    def clear_rag_history(self) -> None:
        """Clear RAG conversation history."""
        self.rag_messages = []
    
    def clear_all_history(self) -> None:
        """Clear all conversation histories."""
        self.ai_messages = []
        self.rag_messages = []


def get_simple_chat_memory(max_history: int = 10) -> SimpleChatMemory:
    """Factory function to create chat memory instance."""
    return SimpleChatMemory(max_history)