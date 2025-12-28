from fastapi import APIRouter, HTTPException
from backend.models.models import ChatRequest, ChatResponse, ErrorResponse, Source
from backend.utils.helpers import process_chat_request, get_chat_history

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def chat(request: ChatRequest):
    """
    Handle chat request and return RAG response
    
    - **message**: User's question (required)
    - **chat_id**: Session ID (optional, will be generated if not provided)
    """
    try:
        # Process request
        chat_id, response_message, sources = process_chat_request(
            message=request.message,
            chat_id=request.chat_id
        )
        
        # Format sources
        formatted_sources = [
            Source(
                text=src["text"],
                score=src["score"],
                url=src.get("url"),
                title=src.get("title")
            )
            for src in sources
        ]
        
        return ChatResponse(
            chat_id=chat_id,
            message=response_message,
            sources=formatted_sources
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Pet Health RAG API"}
