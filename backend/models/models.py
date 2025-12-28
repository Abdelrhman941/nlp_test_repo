from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    chat_id: Optional[str] = Field(None, description="Chat session ID")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What should I feed my dog?",
                "chat_id": "chat_123456"
            }
        }


class Source(BaseModel):
    text: str = Field(..., description="Chunk text")
    score: float = Field(..., description="Relevance score")
    url: Optional[str] = Field(None, description="Source URL")
    title: Optional[str] = Field(None, description="Source title")


class ChatResponse(BaseModel):
    chat_id: str = Field(..., description="Chat session ID")
    message: str = Field(..., description="Assistant response")
    sources: List[Source] = Field(default_factory=list, description="Retrieved sources")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "chat_123456",
                "message": "Dogs should be fed a balanced diet...",
                "sources": [
                    {
                        "text": "Dogs require protein, carbohydrates...",
                        "score": 0.85,
                        "url": "https://petmd.com/dog/nutrition",
                        "title": "Dog Nutrition Guide"
                    }
                ],
                "timestamp": "2025-12-28T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "Message cannot be empty"
            }
        }
