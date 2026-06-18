"""
Simple Multi-Agent API Endpoint for VoltStream.

Provides a unified endpoint for the multi-agent system without complex
routing or event systems.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.agent.agent_coordinator import get_coordinator

router = APIRouter(prefix="/multi-agent", tags=["multi-agent"])


class MultiAgentRequest(BaseModel):
    """Request model for multi-agent endpoint"""
    query: str
    conversation_id: Optional[str] = None


class MultiAgentResponse(BaseModel):
    """Response model for multi-agent endpoint"""
    response: str
    agents_used: List[str]
    success: bool


@router.post("", response_model=MultiAgentResponse)
def process_multi_agent_request(request: MultiAgentRequest) -> MultiAgentResponse:
    """
    Unified endpoint for multi-agent processing.
    
    This endpoint provides a simple interface to the multi-agent system
    without complex workflows or event-driven architecture.
    
    Example request:
        {
            "query": "Optimize my house for energy savings"
        }
    
    Example response:
        {
            "response": "Turned off unnecessary devices... You could save $15/month...",
            "agents_used": ["device", "energy"],
            "success": true
        }
    """
    try:
        coordinator = get_coordinator()
        result = coordinator.process_request(request.query)
        
        return MultiAgentResponse(
            response=result["response"],
            agents_used=result["agents_used"],
            success=result["success"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process multi-agent request: {str(e)}"
        )