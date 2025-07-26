"""
Langfuse service for tracing and observability.
"""

import logging
from contextlib import contextmanager

from config import settings

# Configure logging
logger = logging.getLogger(__name__)


class LangfuseService:
    """Service class for managing Langfuse tracing and observability."""

    def __init__(self):
        """Initialize the Langfuse service."""
        self.client = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize Langfuse client and instrumentation."""
        if not settings.langfuse_enabled:
            logger.info("Langfuse tracing disabled by configuration")
            return False

        try:
            from langfuse import Langfuse
            from pydantic_ai.agent import Agent

            # Initialize Langfuse client using constructor with explicit credentials
            # This avoids the need to set OS environment variables
            self.client = Langfuse(
                public_key=settings.get_langfuse_public_key(),
                secret_key=settings.get_langfuse_secret_key(),
                host=settings.langfuse_host,
            )

            logger.info(f"Langfuse client initialized - Host: {settings.langfuse_host}")

            # Initialize Pydantic AI instrumentation for Langfuse
            Agent.instrument_all()

            self._initialized = True
            logger.info("Langfuse tracing initialized successfully")
            return True

        except ImportError as e:
            logger.warning(f"Langfuse not available: {e}")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            return False

    def is_initialized(self) -> bool:
        """Check if Langfuse is properly initialized."""
        return self._initialized and self.client is not None

    def is_operational(self) -> bool:
        """Check if Langfuse is operational (initialized and authenticated)."""
        if not self.is_initialized():
            return False

        try:
            return self.client.auth_check()
        except Exception as e:
            logger.warning(f"Langfuse auth check failed: {e}")
            return False

    def get_status(self) -> str:
        """Get the current status of Langfuse service."""
        if not settings.langfuse_enabled:
            return "disabled"
        elif not self.is_initialized():
            return "error"
        elif not self.is_operational():
            return "error"
        else:
            return "operational"

    @contextmanager
    def trace_span(self, name: str, **kwargs):
        """Context manager for creating Langfuse spans."""
        if not self.is_initialized():
            # Return a no-op context manager if Langfuse is not available
            yield None
            return

        try:
            with self.client.start_as_current_span(name=name, **kwargs) as span:
                yield span
        except Exception as e:
            logger.warning(f"Failed to create Langfuse span '{name}': {e}")
            yield None

    def update_current_trace(self, **kwargs):
        """Update the current trace with additional attributes."""
        if not self.is_initialized():
            return

        try:
            self.client.update_current_trace(**kwargs)
        except Exception as e:
            logger.warning(f"Failed to update current trace: {e}")


# Global Langfuse service instance
langfuse_service = LangfuseService()
