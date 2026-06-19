from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.services.agentcore_service import AgentCoreService

router = APIRouter(
    prefix="/multi-agent",
    tags=["multi-agent"]
)


class MultiAgentRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


class MultiAgentResponse(BaseModel):
    response: str
    agents_used: List[str]
    success: bool
    session_id: str | None = None
    request_id: str | None = None


@router.post("", response_model=MultiAgentResponse)
def process_multi_agent_request(
    request: MultiAgentRequest
) -> MultiAgentResponse:

    try:

        service = AgentCoreService()

        result = service.invoke(
            request.query
        )

        return MultiAgentResponse(
            response=result["response"],
            agents_used=result["agents_used"],
            success=result["success"],
            session_id=result["session_id"],
            request_id=result["request_id"]
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process multi-agent request: {str(e)}"
        )