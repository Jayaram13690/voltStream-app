"""
FastAPI endpoints for Energy Advisor Agent.

This module provides REST API endpoints for interacting with the Energy
Advisor Agent powered by Amazon Bedrock Nova 2 Lite + Strands Agents SDK.

Focus Areas:
  - Electricity bill reduction advice
  - Energy consumption analysis
  - Solar utilization recommendations
  - Budget monitoring and alerts

POST /energy-advisor        — send an energy advisory request
DELETE /energy-advisor/memory — wipe conversation history
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent import get_energy_advisor

router = APIRouter(prefix="/energy-advisor", tags=["energy-advisor"])


class EnergyAdvisorRequest(BaseModel):
    """Request model for energy advisor endpoint"""
    message: str


class EnergyAdvisorResponse(BaseModel):
    """Response model for energy advisor endpoint"""
    response: str


@router.post("", response_model=EnergyAdvisorResponse)
def process_energy_advisor_request(request: EnergyAdvisorRequest) -> EnergyAdvisorResponse:
    """
    Process an energy advisory request through the Energy Advisor Agent.

    Nova 2 Lite autonomously:
      • Analyzes current energy usage patterns
      • Calculates cost savings opportunities
      • Optimizes solar energy utilization
      • Monitors budget compliance
      • Returns actionable recommendations

    Example request:
        {"message": "How can I reduce my electricity bill?"}

    Example response:
        {"response": "You could save approximately $45/month by:
        1. Reducing Heat pump usage during peak hours (saves ~$20/month)
        2. Optimizing solar battery charging (saves ~$15/month)
        3. Shifting EV charger usage to off-peak hours (saves ~$10/month)"}
    """
    try:
        agent = get_energy_advisor()
        response = agent.process_request(request.message)
        return EnergyAdvisorResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process energy advisor request: {str(e)}",
        )


@router.delete("/memory", status_code=200)
def reset_energy_advisor_memory() -> dict:
    """
    Clear the energy advisor's conversation history.

    Use this to start a fresh energy analysis session without context
    carry-over from earlier interactions.
    """
    try:
        agent = get_energy_advisor()
        agent.reset_memory()
        return {"message": "Energy advisor conversation history cleared successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset energy advisor memory: {str(e)}",
        )