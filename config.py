"""
Configuration management using Pydantic Settings for environment variables.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter API configuration
    openrouter_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="OpenRouter API key"
    )
    
    # Langfuse configuration
    langfuse_public_key: SecretStr = Field(
        default=SecretStr(""),
        description="Langfuse public key"
    )
    langfuse_secret_key: SecretStr = Field(
        default=SecretStr(""),
        description="Langfuse secret key"
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse host URL"
    )
    langfuse_enabled: bool = Field(
        default=True,
        description="Enable Langfuse tracing and monitoring"
    )
    langfuse_trace_content_limit: int = Field(
        default=100,
        description="Maximum characters to trace for message and response content"
    )
    
    # Embedding configuration
    embedding_model_name: str = Field(
        default="BAAI/bge-m3",
        description="HuggingFace embedding model name"
    )
    embedding_device: str = Field(
        default="cpu",
        description="Device for embedding model (cpu, cuda, etc.)"
    )
    
    # Agent configuration
    agent_model_name: str = Field(
        default="google/gemini-2.5-flash-lite",
        description="OpenRouter model name for agent (via OpenAI-compatible interface)"
    )
    agent_temperature: float = Field(
        default=0.7,
        description="Temperature for agent responses (0.0 to 2.0)"
    )
    agent_max_tokens: int = Field(
        default=8192,
        description="Maximum tokens for agent responses"
    )
    
    # Multimodal configuration
    max_image_size_mb: int = Field(
        default=8,
        description="Maximum image size in MB"
    )
    supported_image_formats: list[str] = Field(
        default=["image/jpeg", "image/png", "image/gif"],
        description="Supported image MIME types"
    )
    
    # Application configuration
    app_name: str = Field(
        default="AI Agent API",
        description="Application name"
    )
    app_version: str = Field(
        default="0.1.0",
        description="Application version"
    )
    app_description: str = Field(
        default="AI Agent API Service with embedding and multimodal capabilities",
        description="Application description for FastAPI docs"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    docs_enabled: bool = Field(
        default=True,
        description="Enable FastAPI documentation endpoints (/docs, /redoc)"
    )
    
    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def get_openrouter_api_key(self) -> str:
        """Safely get the OpenRouter API key."""
        return self.openrouter_api_key.get_secret_value()
    
    def get_langfuse_public_key(self) -> str:
        """Safely get the Langfuse public key."""
        return self.langfuse_public_key.get_secret_value()
    
    def get_langfuse_secret_key(self) -> str:
        """Safely get the Langfuse secret key."""
        return self.langfuse_secret_key.get_secret_value()


# Global settings instance
settings = Settings() 