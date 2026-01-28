"""
AI Provider Factory - AI Code Learning Platform

This module provides a factory pattern for creating AI clients based on
the configured provider. Supports switching between Gemini and OpenRouter.

Usage:
    from src.services.ai.provider import get_ai_client, AIProvider

    # Get client based on AI_PROVIDER environment variable
    client = get_ai_client()
    result = await client.generate_content("Explain this code...")

    # Or explicitly specify provider
    client = get_ai_client(AIProvider.OPENROUTER)
"""

import logging
from enum import Enum
from functools import lru_cache
from typing import Any, Protocol

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Supported AI providers."""

    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class AIClientProtocol(Protocol):
    """Protocol defining the interface for AI clients."""

    async def generate_content(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int | None = None,
        response_mime_type: str | None = None,
        response_schema: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> str:
        """Generate text content."""
        ...

    async def generate_json(
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: dict[str, Any] | None = None,
        temperature: float = 0.5,
        max_output_tokens: int | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Generate JSON content."""
        ...

    async def check_health(self) -> dict[str, Any]:
        """Check API health."""
        ...


class AIProviderSettings(BaseSettings):
    """
    AI Provider selection settings.

    Environment Variables:
        AI_PROVIDER: Provider to use (gemini | openrouter)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ai_provider: AIProvider = Field(
        default=AIProvider.OPENROUTER,
        description="AI provider to use (gemini or openrouter)",
    )


@lru_cache
def get_provider_settings() -> AIProviderSettings:
    """Get cached provider settings."""
    return AIProviderSettings()


def get_ai_client(provider: AIProvider | None = None) -> AIClientProtocol:
    """
    Get an AI client instance based on provider.

    Args:
        provider: Optional provider to use. If not specified,
                  uses AI_PROVIDER environment variable.

    Returns:
        AIClientProtocol: Configured AI client instance

    Raises:
        ValueError: If the provider is not supported
    """
    if provider is None:
        provider = get_provider_settings().ai_provider

    logger.info(f"Creating AI client for provider: {provider.value}")

    if provider == AIProvider.GEMINI:
        from src.services.ai.gemini_client import get_gemini_client

        return get_gemini_client()

    elif provider == AIProvider.OPENROUTER:
        from src.services.ai.openrouter_client import get_openrouter_client

        return get_openrouter_client()

    else:
        raise ValueError(f"Unsupported AI provider: {provider}")


# Convenience aliases for error classes
def get_ai_error_classes(provider: AIProvider | None = None):
    """
    Get error classes for the specified provider.

    Returns a dict with common error types mapped to provider-specific classes.
    """
    if provider is None:
        provider = get_provider_settings().ai_provider

    if provider == AIProvider.GEMINI:
        from src.services.ai.gemini_client import (
            GeminiAPIError,
            GeminiContentBlockedError,
            GeminiError,
            GeminiInvalidResponseError,
            GeminiRateLimitError,
            GeminiTimeoutError,
        )

        return {
            "base": GeminiError,
            "api": GeminiAPIError,
            "rate_limit": GeminiRateLimitError,
            "timeout": GeminiTimeoutError,
            "content_blocked": GeminiContentBlockedError,
            "invalid_response": GeminiInvalidResponseError,
        }

    elif provider == AIProvider.OPENROUTER:
        from src.services.ai.openrouter_client import (
            OpenRouterAPIError,
            OpenRouterContentBlockedError,
            OpenRouterError,
            OpenRouterInvalidResponseError,
            OpenRouterRateLimitError,
            OpenRouterTimeoutError,
        )

        return {
            "base": OpenRouterError,
            "api": OpenRouterAPIError,
            "rate_limit": OpenRouterRateLimitError,
            "timeout": OpenRouterTimeoutError,
            "content_blocked": OpenRouterContentBlockedError,
            "invalid_response": OpenRouterInvalidResponseError,
        }

    else:
        raise ValueError(f"Unsupported AI provider: {provider}")
