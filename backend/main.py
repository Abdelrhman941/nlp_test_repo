from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config import CORS_ORIGINS
import uvicorn

app = FastAPI(
    title="Pet Health RAG API",
    description="RAG-powered chatbot API for pet health questions",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Pet Health RAG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    from backend.config import API_HOST, API_PORT, API_RELOAD
    
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
