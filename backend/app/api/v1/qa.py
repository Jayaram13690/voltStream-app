from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import services using absolute paths from app directory
from app.services.rag_service import RAGService
from app.services.bedrock_service import BedrockService
from app.services.auto_ingest_service import AutoIngestService

router = APIRouter()

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    answer: str
    context_used: Optional[str] = None

@router.post("/qa")
async def answer_question(request: QARequest):
    """Enhanced QA endpoint with automatic ingestion"""
    try:
        # Initialize auto-ingestion service
        auto_ingest = AutoIngestService()
        auto_ingest.auto_ingest_if_changed()

        # Proceed with RAG as usual
        rag_service = RAGService()
        bedrock_service = BedrockService()
        
        context = rag_service.get_retrieved_context(request.question)
        
        if context == "NO_RELEVANT_CONTEXT_FOUND":
            return {
                "answer": "I don't have that information.",
                "context_used": "No relevant context found in knowledge base"
            }
        
        prompt = rag_service.generate_rag_prompt(request.question, context)
        answer = bedrock_service.generate_rag_response(prompt)
        
        return {
            "answer": answer,
            "context_used": context[:500] + "..." if len(context) > 500 else context
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing error: {str(e)}"
        )