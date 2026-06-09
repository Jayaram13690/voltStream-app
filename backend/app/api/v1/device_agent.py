"""
FastAPI endpoints for Device Control Agent.

This module provides REST API endpoints for interacting with the Device Control Agent
that uses Strands Agents SDK and Amazon Bedrock Nova Lite.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent import get_device_agent

router = APIRouter(prefix="/agent", tags=["device-agent"])


class AgentRequest(BaseModel):
    """Request model for agent endpoint"""
    message: str


class AgentResponse(BaseModel):
    """Response model for agent endpoint"""
    response: str


@router.post("", response_model=AgentResponse)
def process_agent_request(request: AgentRequest) -> AgentResponse:
    """
    Process a natural language request through the Device Control Agent.
    
    Example request:
    {
        "message": "Turn off the dishwasher"
    }
    
    Example response:
    {
        "response": "The dishwasher was online and has now been turned off."
    }
    """
    try:
        # Get device agent instance
        agent = get_device_agent()
        
        # Process the user request
        response = agent.process_request(request.message)
        
        return AgentResponse(response=response)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process agent request: {str(e)}"
        )