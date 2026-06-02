"""
Pydantic models for chat functionality.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str