"""
FastAPI endpoints for Device Control Agent.

This module provides REST API endpoints for interacting with the Device
Control Agent powered by Amazon Bedrock Nova 2 Lite + Strands Agents SDK.

POST /agent        — send a natural language message
DELETE /agent/memory — wipe conversation history
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
    Process a natural language device-control request through the 90 %
    agentic Device Control Agent.

    Nova 2 Lite autonomously:
      • Discovers relevant devices via list_devices
      • Resolves device names / pronouns using conversation history
      • Selects the appropriate tool(s)
      • Executes multi-step ReAct workflows
      • Returns a concise confirmation

    Example request:
        {"message": "Turn off all online devices"}

    Example response:
        {"response": "Done! I turned off Dishwasher (was online) and Fan (was online)."}
    """
    try:
        agent = get_device_agent()
        response = agent.process_request(request.message)
        return AgentResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process agent request: {str(e)}",
        )


@router.delete("/memory", status_code=200)
def reset_agent_memory() -> dict:
    """
    Clear the agent's conversation history.

    Use this to start a fresh session without pronoun / context carry-over
    from earlier interactions.
    """
    try:
        agent = get_device_agent()
        agent.reset_memory()
        return {"message": "Conversation history cleared successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset agent memory: {str(e)}",
        )