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
        default="AI Agent API Service with embedding capabilities",
        description="Application description for FastAPI docs"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    
    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
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