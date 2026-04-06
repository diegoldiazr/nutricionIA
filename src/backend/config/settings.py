"""
Centralized Configuration Management using Pydantic Settings.

All configuration is loaded from environment variables.
Environment variables can be set in .env file or exported in shell.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional
import os


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    url: str = Field(
        default="sqlite:///./data/nutrition.db",
        description="Database connection URL"
    )
    pool_size: int = Field(default=5, description="Connection pool size")
    echo: bool = Field(default=False, description="Enable SQL echo logging")


class OpenRouterSettings(BaseSettings):
    """OpenRouter AI API configuration."""
    model_config = SettingsConfigDict(env_prefix="OPENROUTER_")

    api_key: str = Field(
        default="",
        description="OpenRouter API key"
    )
    model: str = Field(
        default="claude-sonnet-4-20260414",
        description="Default AI model ID"
    )
    site_url: str = Field(
        default="http://localhost:8000",
        description="Site URL for API referer"
    )
    site_name: str = Field(
        default="Nutrition AI Assistant",
        description="Site name for API title"
    )
    timeout: float = Field(default=60.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class NotebookLMSettings(BaseSettings):
    """NotebookLM knowledge base configuration."""
    model_config = SettingsConfigDict(env_prefix="NOTEBOOKLM_")

    api_url: str = Field(
        default="https://notebooklm.googleapis.com/v1",
        description="NotebookLM API base URL"
    )
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class NotionSettings(BaseSettings):
    """Notion integration configuration (for NotebookLM auth)."""
    model_config = SettingsConfigDict(env_prefix="NOTION_")

    token: str = Field(
        default="",
        description="Notion integration token"
    )
    workspace: str = Field(
        default="",
        description="Notion workspace ID"
    )


class Settings(BaseSettings):
    """
    Main application settings.

    Combines all configuration sections.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    app_name: str = Field(default="Nutrition AI Assistant", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    DATABASE: DatabaseSettings = Field(default_factory=DatabaseSettings)
    OPENROUTER: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    NOTEBOOKLM: NotebookLMSettings = Field(default_factory=NotebookLMSettings)
    NOTION: NotionSettings = Field(default_factory=NotionSettings)


# Global settings instance
settings = Settings()
