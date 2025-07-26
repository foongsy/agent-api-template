"""
Agent implementation using pydantic-ai framework with OpenRouter + Gemini integration.
"""

import logging
import time
from typing import List, Optional

from pydantic_ai import Agent, BinaryContent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from config import settings
from langfuse_service import langfuse_service
from models import AgentResponse, ChatRequest

# Configure logging
logger = logging.getLogger(__name__)


class AgentService:
    """Service class for managing pydantic-ai agents with multimodal support."""

    def __init__(self):
        """Initialize the agent service."""
        self.agent = None
        self._setup_agent()

    def _setup_agent(self):
        """Setup the pydantic-ai agent with OpenRouter + Gemini integration."""
        try:
            logger.info(f"Initializing agent with model: {settings.agent_model_name}")

            # Create OpenRouter provider
            provider = OpenRouterProvider(api_key=settings.get_openrouter_api_key())

            # Create OpenAI-compatible model for Gemini via OpenRouter
            model = OpenAIModel(settings.agent_model_name, provider=provider)

            # Create agent with structured output
            self.agent = Agent(
                model=model,
                output_type=AgentResponse,
                instructions=(
                    "You are a helpful AI assistant. Provide clear, accurate, and helpful responses. "
                    "When analyzing images, describe what you see and answer questions about the content. "
                    "Always respond in a structured format with clear content and reasoning when appropriate."
                ),
                instrument=langfuse_service.is_initialized(),  # Only enable instrumentation if Langfuse is initialized
            )

            logger.info("Agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            raise RuntimeError(f"Failed to initialize agent: {str(e)}")

    def _validate_images(
        self, images: Optional[List[bytes]], mime_types: Optional[List[str]]
    ) -> List[BinaryContent]:
        """Validate and prepare images for multimodal input using pydantic-ai BinaryContent."""
        if not images:
            return []

        if not mime_types or len(images) != len(mime_types):
            raise ValueError("Number of images must match number of MIME types")

        validated_images = []
        max_size_bytes = settings.max_image_size_mb * 1024 * 1024

        for i, (image_bytes, mime_type) in enumerate(zip(images, mime_types)):
            # Validate MIME type
            if mime_type not in settings.supported_image_formats:
                raise ValueError(
                    f"Unsupported image format: {mime_type}. Supported: {settings.supported_image_formats}"
                )

            # Validate size
            if len(image_bytes) > max_size_bytes:
                raise ValueError(
                    f"Image {i} exceeds maximum size of {settings.max_image_size_mb}MB"
                )

            # Create BinaryContent for pydantic-ai
            validated_images.append(
                BinaryContent(data=image_bytes, media_type=mime_type)
            )

        return validated_images

    async def process_message(self, request: ChatRequest) -> AgentResponse:
        """Process a message through the agent with optional multimodal input."""
        start_time = time.time()

        # Add Langfuse tracing
        with langfuse_service.trace_span("agent.process_message") as span:
            try:
                logger.info(f"Processing message (length: {len(request.message)})")

                # Update trace with request details (truncated content, excluding images)
                if span:
                    # Truncate message content for tracing
                    truncated_message = (
                        request.message[: settings.langfuse_trace_content_limit] + "..."
                        if len(request.message) > settings.langfuse_trace_content_limit
                        else request.message
                    )

                    langfuse_service.update_current_trace(
                        input={
                            "message": truncated_message,
                            "message_length": len(request.message),
                            "has_images": bool(request.images),
                        },
                        tags=["agent", "chat"],
                        metadata={"session_id": request.session_id},
                    )

                # Validate and prepare images if provided
                images = []
                if request.images:
                    logger.info(f"Processing {len(request.images)} images")
                    images = self._validate_images(
                        request.images, request.image_mime_types
                    )

                # Prepare input for agent
                if images:
                    # Multimodal input with images - combine text and images in a list
                    input_content = [request.message] + images
                    result = await self.agent.run(input_content)
                else:
                    # Text-only input
                    result = await self.agent.run(request.message)

                processing_time = (time.time() - start_time) * 1000
                logger.info(f"Agent response generated in {processing_time:.2f}ms")

                # Update trace with response details (truncated content)
                if span:
                    # Truncate response content for tracing
                    truncated_response = (
                        result.output.content[: settings.langfuse_trace_content_limit]
                        + "..."
                        if len(result.output.content)
                        > settings.langfuse_trace_content_limit
                        else result.output.content
                    )

                    langfuse_service.update_current_trace(
                        output={
                            "response": truncated_response,
                            "processing_time_ms": processing_time,
                            "response_length": len(result.output.content),
                        },
                        metadata={"model_used": settings.agent_model_name},
                    )

                return result.output

            except UnexpectedModelBehavior as e:
                logger.error(f"Model behavior error: {str(e)}")
                raise RuntimeError(f"Model error: {str(e)}")
            except ValueError as e:
                logger.error(f"Validation error: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in agent processing: {str(e)}")
                raise RuntimeError(f"Agent processing error: {str(e)}")

    async def validate_agent(self) -> bool:
        """Validate that the agent can process messages correctly."""
        try:
            logger.info("Validating agent...")

            # Check if we have an API key
            api_key = settings.get_openrouter_api_key()
            if not api_key or api_key.strip() == "":
                logger.warning(
                    "No OpenRouter API key provided. Skipping live agent validation."
                )
                logger.info("Agent configuration validation successful (no API key)")
                return True

            # Test with a simple message
            test_request = ChatRequest(message="Hello, this is a test message.")
            result = await self.process_message(test_request)

            if not isinstance(result, AgentResponse):
                raise RuntimeError("Agent did not return expected structured output")

            logger.info("Agent validation successful")
            return True

        except Exception as e:
            logger.error(f"Agent validation failed: {str(e)}")
            raise RuntimeError(f"Agent validation failed: {str(e)}")


# Global agent service instance
agent_service = AgentService()
