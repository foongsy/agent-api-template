"""
AI Agent API Service - Main FastAPI application.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from agent import agent_service

# Import after environment variables are loaded by pydantic-settings
from config import settings
from embeddings import embedding_service
from langfuse_service import langfuse_service
from models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    HealthResponse,
)

# Configure logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""

    # Startup: Initialize and validate services
    logger.info("Starting up AI Agent API Service...")

    # Initialize Langfuse service
    langfuse_service.initialize()

    try:
        # Validate embedding service
        logger.info("Validating embedding service...")
        await embedding_service.validate_model()
        logger.info("Embedding service validation successful")

        # Validate agent service
        logger.info("Validating agent service...")
        await agent_service.validate_agent()
        logger.info("Agent service validation successful")

        logger.info(
            "All services validated successfully. Application ready to serve requests."
        )

    except Exception as e:
        logger.error(f"Service validation failed: {str(e)}")
        raise RuntimeError(f"Failed to start application: {str(e)}")

    yield

    # Shutdown: Cleanup resources
    logger.info("Shutting down AI Agent API Service...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check service status
        services = {
            "agent": "operational",
            "embeddings": "operational",
            "langfuse": langfuse_service.get_status(),
        }

        return HealthResponse(
            status="healthy",
            services=services,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/api/v1/agent/chat", response_model=ChatResponse)
async def chat_with_agent(
    message: str = Form(..., description="Text message from user"),
    session_id: Optional[str] = Form(None, description="Session identifier"),
    images: Optional[List[UploadFile]] = File(None, description="Images to analyze"),
):
    """Chat with the AI agent with optional multimodal input."""
    start_time = time.time()

    try:
        # Validate message
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(message) > 10000:
            raise HTTPException(
                status_code=400, detail="Message too long (max 10,000 characters)"
            )

        # Process images if provided
        image_bytes = []
        image_mime_types = []

        if images:
            for i, image in enumerate(images):
                # Validate file size
                if image.size > settings.max_image_size_mb * 1024 * 1024:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image {i+1} exceeds maximum size of {settings.max_image_size_mb}MB",
                    )

                # Validate MIME type
                if image.content_type not in settings.supported_image_formats:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported image format: {image.content_type}. Supported: {settings.supported_image_formats}",
                    )

                # Read image bytes
                content = await image.read()
                image_bytes.append(content)
                image_mime_types.append(image.content_type)

        # Create request object
        request = ChatRequest(
            message=message.strip(),
            images=image_bytes if image_bytes else None,
            image_mime_types=image_mime_types if image_mime_types else None,
            session_id=session_id,
        )

        logger.info(
            f"Processing chat request (text: {len(message)} chars, images: {len(image_bytes)})"
        )

        # Process with agent
        agent_response = await agent_service.process_message(request)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Chat response generated in {processing_time_ms:.2f}ms")

        return ChatResponse(
            response=agent_response,
            session_id=session_id,
            processing_time_ms=processing_time_ms,
            model_used=settings.agent_model_name,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/api/v1/embeddings", response_model=EmbeddingResponse)
async def get_embeddings(request: EmbeddingRequest):
    """Generate embeddings for input text."""
    start_time = time.time()

    try:
        # Input validation
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(request.text) > 10000:  # Reasonable limit for embedding text
            raise HTTPException(
                status_code=400, detail="Text too long (max 10,000 characters)"
            )

        logger.info(f"Generating embeddings for text (length: {len(request.text)})")

        # Generate embeddings
        embeddings = await embedding_service.get_embeddings(request.text)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Generated embeddings successfully in {processing_time_ms:.2f}ms")

        return EmbeddingResponse(
            embeddings=embeddings,
            model=settings.embedding_model_name,
            dimensions=len(embeddings),
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Agent API Service",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
