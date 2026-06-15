"""
Chat API endpoints using AWS Bedrock.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.bedrock_service import generate_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint that uses AWS Bedrock to generate responses.
    
    Args:
        request (ChatRequest): Contains the question to ask
        
    Returns:
        ChatResponse: Contains the generated answer
        
    Raises:
        HTTPException: If there's an error generating the response
    """
    try:
        # Generate response using Bedrock service
        answer = generate_response(request.question)
        
        return ChatResponse(answer=answer)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")