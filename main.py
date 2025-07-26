"""
AI Agent API Service - Flask application.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from flask import Flask, request
from flask_cors import CORS
from flask_pydantic import validate

# Import after environment variables are loaded by pydantic-settings
from agent import agent_service
from config import settings
from embeddings import embedding_service
from langfuse_service import langfuse_service
from models import (
    AgentResponse,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    HealthResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Flask app
app.config.update(
    {
        "DEBUG": settings.debug,
        "TESTING": False,
    }
)

# Add CORS middleware
CORS(
    app,
    origins=["*"],  # Configure appropriately for production
    allow_headers=["*"],
    methods=["*"],
    supports_credentials=True,
)


# Application startup and shutdown handlers
startup_completed = False


def initialize_services():
    """Initialize and validate services."""
    global startup_completed
    if startup_completed:
        return

    logger.info("Starting up AI Agent API Service (Flask)...")

    # Initialize Langfuse service
    langfuse_service.initialize()

    try:
        # Validate embedding service
        logger.info("Validating embedding service...")
        asyncio.run(embedding_service.validate_model())
        logger.info("Embedding service validation successful")

        # Validate agent service
        logger.info("Validating agent service...")
        asyncio.run(agent_service.validate_agent())
        logger.info("Agent service validation successful")

        logger.info(
            "All services validated successfully. Application ready to serve requests."
        )
        startup_completed = True

    except Exception as e:
        logger.error(f"Service validation failed: {str(e)}")
        raise RuntimeError(f"Failed to start application: {str(e)}")


@app.teardown_appcontext
def shutdown(error):
    """Cleanup resources on application shutdown."""
    if error:
        logger.error(f"Application error during shutdown: {error}")
    logger.info("Shutting down AI Agent API Service (Flask)...")


# API Routes
@app.route("/api/v1/health", methods=["GET"])
@validate()
def health_check() -> HealthResponse:
    """Health check endpoint."""
    initialize_services()
    
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
        ).model_dump()
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"error": "Health check failed"}, 500


@app.route("/api/v1/embeddings", methods=["POST"])
@validate()
def get_embeddings(body: EmbeddingRequest) -> EmbeddingResponse:
    """Generate embeddings for input text."""
    initialize_services()
    start_time = time.time()

    try:
        # Input validation
        if not body.text or not body.text.strip():
            return {"error": "Text cannot be empty"}, 400

        if len(body.text) > 10000:  # Reasonable limit for embedding text
            return {"error": "Text too long (max 10,000 characters)"}, 400

        logger.info(f"Generating embeddings for text (length: {len(body.text)})")

        # Generate embeddings
        embeddings = asyncio.run(embedding_service.get_embeddings(body.text))

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Generated embeddings successfully in {processing_time_ms:.2f}ms")

        return EmbeddingResponse(
            embeddings=embeddings,
            model=settings.embedding_model_name,
            dimensions=len(embeddings),
            processing_time_ms=processing_time_ms,
        ).model_dump()

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        return {"error": f"Embedding error: {str(e)}"}, 500


def validate_flask_files(files):
    """Convert Flask FileStorage to bytes and MIME types"""
    image_bytes = []
    mime_types = []
    
    for file in files:
        if file.filename:
            content = file.read()
            image_bytes.append(content)
            mime_types.append(file.content_type)
    
    return image_bytes, mime_types


@app.route("/api/v1/agent/chat", methods=["POST"])
def chat_with_agent():
    """Chat with the AI agent with optional multimodal input."""
    initialize_services()
    start_time = time.time()
    
    try:
        # Get form data
        message = request.form.get('message')
        session_id = request.form.get('session_id')
        
        # Validate message
        if not message or not message.strip():
            return {"detail": "Message cannot be empty"}, 400
        
        if len(message) > 10000:
            return {"detail": "Message too long (max 10,000 characters)"}, 400
        
        # Process images if provided
        image_bytes = []
        image_mime_types = []
        
        if 'images' in request.files:
            files = request.files.getlist('images')
            for i, file in enumerate(files):
                if file.filename:  # Check if file was actually uploaded
                    # Validate file size
                    file.seek(0, 2)  # Seek to end to get size
                    size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if size > settings.max_image_size_mb * 1024 * 1024:
                        return {
                            "detail": f"Image {i+1} exceeds maximum size of {settings.max_image_size_mb}MB"
                        }, 400
                    
                    # Validate MIME type
                    if file.content_type not in settings.supported_image_formats:
                        return {
                            "detail": f"Unsupported image format: {file.content_type}. Supported: {settings.supported_image_formats}"
                        }, 400
                    
                    # Read image bytes
                    content = file.read()
                    image_bytes.append(content)
                    image_mime_types.append(file.content_type)
        
        # Create request object
        chat_request = ChatRequest(
            message=message.strip(),
            images=image_bytes if image_bytes else None,
            image_mime_types=image_mime_types if image_mime_types else None,
            session_id=session_id
        )
        
        logger.info(f"Processing chat request (text: {len(message)} chars, images: {len(image_bytes)})")
        
        # Process with agent
        agent_response = asyncio.run(agent_service.process_message(chat_request))
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Chat response generated in {processing_time_ms:.2f}ms")
        
        response = ChatResponse(
            response=agent_response,
            session_id=session_id,
            processing_time_ms=processing_time_ms,
            model_used=settings.agent_model_name
        )
        
        return response.model_dump()
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"detail": str(e)}, 400
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        return {"detail": f"Agent error: {str(e)}"}, 500


@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Agent API Service (Flask)",
        "version": settings.app_version,
        "docs": "/docs" if settings.docs_enabled else None,
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    # For development - use Gunicorn for production
    app.run(
        host=getattr(settings, "flask_host", "0.0.0.0"),
        port=getattr(settings, "flask_port", 8000),
        debug=settings.debug,
    ) 