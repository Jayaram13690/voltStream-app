from typing import List, Dict, Any
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
    
    def retrieve_context(self, question: str, k: int = 3) -> str:
        """Retrieve and format context with confidence filtering"""
        question_embedding = self.embedding_service.generate_embedding(question)
        if not question_embedding:
            return ""
        
        results = self.vector_store.search(question, k, query_embedding=question_embedding)
        
        # If no results pass confidence threshold
        if not results:
            return "NO_RELEVANT_CONTEXT_FOUND"
        
        # Format retrieved context with distances
        context = "\n\n".join([
            f"CONTEXT {i+1}:\n{result['content'].strip()}"
            for i, result in enumerate(results)
        ])
        
        return context
    
    def generate_rag_prompt(self, question: str, context: str) -> str:
        """Generate RAG prompt with strict context usage instructions"""
        return f"""You are a RAG assistant.

Use ONLY the information provided in CONTEXT.

If the answer is present in the context,
answer using the context.

If the answer is not present in the context,
respond exactly:

I don't have that information.

Do not use prior knowledge.
Do not invent facts.
Do not answer from memory.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    
    def get_retrieved_context(self, question: str) -> str:
        """Get retrieved context with validation"""
        context = self.retrieve_context(question)
        if not context.strip():
            return "NO_RELEVANT_CONTEXT_FOUND"
        return context