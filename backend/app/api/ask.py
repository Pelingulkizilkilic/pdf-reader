# app/api/ask.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.auth import get_current_user
from app.state import hybrid_state
from app.services.openai_service import openai_service

router = APIRouter()


class QuestionRequest(BaseModel):
    pdf_id: str
    question: str
    top_k: int = 3
    model: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ConversationRequest(BaseModel):
    pdf_id: str
    messages: List[ChatMessage]
    model: Optional[str] = None


@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Ask a question about a PDF"""
    try:
        pdf_id = request.pdf_id
        question = request.question
        top_k = request.top_k
        
        # 1. Check if PDF exists
        pdf_info = hybrid_state.get_pdf(pdf_id)
        if not pdf_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not found"
            )
        
        # 2. Get vector store
        vector_store = hybrid_state.get_vector_store(pdf_id)
        if not vector_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF not processed yet or vector database missing"
            )
        
        # 3. Search for similar chunks (RAG)
        from app.rag.vector_store import search_similar_chunks
        similar_chunks = search_similar_chunks(
            vector_store=vector_store,
            question=question,
            k=top_k
        )
        
        if not similar_chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant information found in PDF"
            )
        
        # 4. Prepare context from chunks
        context = "\n\n".join([
            f"[Source {i+1}]: {chunk['text']}"
            for i, chunk in enumerate(similar_chunks)
        ])
        
        # 5. Get answer from OpenAI
        openai_response = await openai_service.generate_answer(
            question=question,
            context=context,
            model=request.model
        )
        
        # 6. Prepare response
        response_data = {
            "question": question,
            "pdf_id": pdf_id,
            "pdf_name": pdf_info.get("filename", "Unknown"),
            "answer": openai_response["answer"],
            "model_used": openai_response["model"],
            "is_mock_response": openai_response.get("is_mock", False),
            "relevant_chunks": [
                {
                    "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                    "similarity_score": chunk.get("distance", 0),
                    "rank": chunk.get("rank", i + 1)
                }
                for i, chunk in enumerate(similar_chunks)
            ],
            "chunks_used": len(similar_chunks),
            "tokens_used": openai_response.get("usage", {}).get("total_tokens", 0)
        }
        
        # Add warning if mock mode
        if openai_response.get("is_mock", False):
            response_data["warning"] = "Using mock responses. Add OpenAI API key for real AI answers."
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error asking question: {str(e)}"
        )


@router.get("/models")
async def list_available_models(
    current_user: dict = Depends(get_current_user)
):
    """List available OpenAI models"""
    api_check = await openai_service.check_api_key()
    
    if api_check.get("mock_mode", True):
        return {
            "available": False,
            "message": "OpenAI API key not configured",
            "models": ["mock-gpt-3.5-turbo"],
            "suggestion": "Add OPENAI_API_KEY to .env file"
        }
    
    return {
        "available": api_check["valid"],
        "message": api_check["message"],
        "models": api_check.get("models_available", []),
        "default_model": openai_service.default_model,
        "embedding_model": openai_service.embedding_model
    }


@router.get("/openai/status")
async def check_openai_status():
    """Check OpenAI API status"""
    return await openai_service.check_api_key()