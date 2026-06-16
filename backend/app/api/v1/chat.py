"""
Chat API endpoints using dedicated ChatService (not RAG).
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize dedicated chat service (separate from RAG)
chat_service = ChatService()


@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    General AI Chat endpoint.
    
    Uses pure LLM conversation with history, no document retrieval.
    Can answer general knowledge questions about any topic.
    
    Args:
        request (ChatRequest): Contains the question to ask
        
    Returns:
        ChatResponse: Contains the generated answer
        
    Raises:
        HTTPException: If there's an error generating the response
    """
    try:
        # Use dedicated chat service (not RAG)
        answer = chat_service.chat(request.question)
        
        return ChatResponse(answer=answer)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@router.post("/clear", response_model=dict)
def clear_chat_history():
    """Clear the general AI chat conversation history."""
    try:
        chat_service.clear_history()
        return {"status": "success", "message": "General chat history cleared"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat history: {str(e)}"
        )