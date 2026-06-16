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

# Security: Forbidden query patterns
FORBIDDEN_PATTERNS = [
    "who are you", "what are you", "tell me about yourself",
    "show context", "show documents", "show prompt",
    "ignore the documents", "forget the documents",
    "tell me a joke", "what's your name",
    "what information do you have", "what can you do",
    "list the documents", "describe your capabilities",
    "your instructions", "your prompt", "your system",
    "reveal context", "display context", "show me the chunks"
]

def is_allowed_question(question: str) -> bool:
    """Check if question violates security rules"""
    lower_q = question.lower().strip()

    # Block meta-questions
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in lower_q:
            return False

    # Must be a question or document query - be more lenient
    # Allow any reasonable query that doesn't contain forbidden patterns
    if not lower_q.strip():
        return False
    
    # Basic length check
    if len(lower_q.split()) < 2:  # At least 2 words
        return False

    return True

@router.post("/qa")
async def answer_question(request: QARequest):
    """Strict document-only QA with isolated conversation history and security validation"""
    try:
        question = request.question.strip()
        print(f"=== STARTING QA PROCESSING FOR: '{question}' ===")

        # Security validation first - block forbidden patterns
        if not is_allowed_question(question):
            return {
                "answer": "Please ask a question related to the uploaded document.",
                "context_used": "Query violates document-only constraints."
            }

        # Initialize auto-ingestion service with correct path
        auto_ingest = AutoIngestService('app/document/Solar_Energy_Report.pdf')
        auto_ingest.auto_ingest_if_changed()

        # Use RAG service with isolated conversation history
        rag_service = RAGService()
        
        # First get retrieved context from documents
        print(f"DEBUG: QA endpoint calling get_retrieved_context with threshold: 0.4")
        context = rag_service.get_retrieved_context(question, confidence_threshold=0.4)
        print(f"DEBUG: QA endpoint received context: '{context[:50]}...'" if len(context) > 50 else f"DEBUG: QA endpoint received context: '{context}'")
        
        if context == "NO_RELEVANT_CONTEXT_FOUND":
            print("DEBUG: QA endpoint returning 'no information' response")
            print(f"=== QA PROCESSING COMPLETED - NO CONTEXT FOUND FOR: '{question}' ===")
            return {
                "answer": "I don't have that information.",
                "context_used": "No relevant document context found."
            }
        
        # Now use chat_rag method which handles both document context AND conversation history
        answer = rag_service.chat_rag(question)
        
        # Post-processing: Ensure no context leakage
        answer_lower = answer.lower()
        leakage_detected = any(leak in answer_lower for leak in ["context:", "document:", "retrieved:", "based on the context"])
        if leakage_detected:
            print(f"DEBUG: Context leakage detected in response")
            return {
                "answer": "I don't have that information.",
                "context_used": "Response violated document constraints."
            }
        
        print(f"DEBUG: Returning successful response to user")
        print(f"=== QA PROCESSING COMPLETED SUCCESSFULLY FOR: '{question}' ===")
        return {
            "answer": answer,
            "context_used": "Document context retrieved and used with isolated RAG history."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing error: {str(e)}"
        )


@router.post("/qa/clear")
async def clear_rag_history():
    """Clear the RAG conversation history."""
    try:
        rag_service = RAGService()
        rag_service.chat_memory.clear_rag_history()
        return {"status": "success", "message": "RAG chat history cleared"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear RAG history: {str(e)}"
        )