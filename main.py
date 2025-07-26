"""
AI Agent API Service - Main FastAPI application.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Import after environment variables are loaded by pydantic-settings
from config import settings
from agent import agent_service
from embeddings import embedding_service


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    embeddings: List[float]
    model: str = "BAAI/bge-m3"


class HealthResponse(BaseModel):
    status: str
    services: dict
    timestamp: str


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # TODO: Implement actual health checks in Milestone 5
    return HealthResponse(
        status="healthy",
        services={
            "agent": "operational",
            "embeddings": "operational",
            "langfuse": "operational"
        },
        timestamp="2025-01-27T00:00:00Z"
    )


@app.post("/api/v1/agent/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the AI agent."""
    try:
        # TODO: Implement actual agent processing in Milestone 4
        response = await agent_service.process_message(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/api/v1/embeddings", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    """Generate embeddings for input text."""
    try:
        # TODO: Implement actual embedding generation in Milestone 2
        embeddings = await embedding_service.get_embeddings(request.text)
        return EmbeddingResponse(
            embeddings=embeddings,
            model="BAAI/bge-m3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Agent API Service",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
