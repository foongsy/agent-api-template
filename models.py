"""
Pydantic models for structured output and request/response handling.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Structured response from the AI agent."""

    content: str = Field(..., description="The main response content from the agent")
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score of the response"
    )
    reasoning: Optional[str] = Field(None, description="Agent's reasoning process")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(
        ..., min_length=1, max_length=10000, description="Text message from user"
    )
    images: Optional[List[bytes]] = Field(
        None, description="List of image bytes (JPEG, PNG, GIF)"
    )
    image_mime_types: Optional[List[str]] = Field(
        None, description="MIME types for each image"
    )
    session_id: Optional[str] = Field(
        None, description="Session identifier (for future use)"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: AgentResponse = Field(..., description="Structured agent response")
    session_id: Optional[str] = Field(None, description="Session identifier")
    processing_time_ms: float = Field(
        ..., description="Processing time in milliseconds"
    )
    model_used: str = Field(..., description="Model used for generation")


class EmbeddingRequest(BaseModel):
    """Request model for embedding endpoint."""

    text: str = Field(..., min_length=1, max_length=10000, description="Text to embed")


class EmbeddingResponse(BaseModel):
    """Response model for embedding endpoint."""

    embeddings: List[float] = Field(..., description="Generated embeddings")
    model: str = Field(..., description="Model used for embedding")
    dimensions: int = Field(..., description="Number of embedding dimensions")
    processing_time_ms: float = Field(
        ..., description="Processing time in milliseconds"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    services: dict = Field(..., description="Status of individual services")
    timestamp: str = Field(..., description="Timestamp of health check")
