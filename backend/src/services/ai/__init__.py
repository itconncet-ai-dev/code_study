"""
AI Services Package - LLM integration for document and answer generation.

This package provides wrappers and utilities for AI-powered content generation
using multiple AI providers (Google Gemini, OpenRouter).

Modules:
    gemini_client: Async-compatible Gemini API wrapper with retry logic
    openrouter_client: Async-compatible OpenRouter API wrapper with retry logic
    provider: Factory pattern for selecting AI provider
    prompts: Prompt templates for document, practice, and Q&A generation

Usage:
    # Recommended: Use the provider factory (respects AI_PROVIDER env var)
    from src.services.ai import get_ai_client

    client = get_ai_client()
    result = await client.generate_content("Explain this code...")

    # Or use specific providers directly
    from src.services.ai import get_gemini_client, get_openrouter_client
"""

# Gemini client
from src.services.ai.gemini_client import (
    GeminiAPIError,
    GeminiClient,
    GeminiContentBlockedError,
    GeminiError,
    GeminiInvalidResponseError,
    GeminiRateLimitError,
    GeminiSettings,
    GeminiTimeoutError,
    get_gemini_client,
    get_gemini_settings,
)

# OpenRouter client
from src.services.ai.openrouter_client import (
    OpenRouterAPIError,
    OpenRouterClient,
    OpenRouterContentBlockedError,
    OpenRouterError,
    OpenRouterInvalidResponseError,
    OpenRouterRateLimitError,
    OpenRouterSettings,
    OpenRouterTimeoutError,
    get_openrouter_client,
    get_openrouter_settings,
)

# Prompt templates
from src.services.ai.prompts import (
    DOCUMENT_RESPONSE_SCHEMA,
    EDUCATIONAL_SYSTEM_INSTRUCTION,
    KOREAN_EDUCATIONAL_SYSTEM_INSTRUCTION,
    DocumentPrompts,
    FileInfo,
    estimate_token_count,
    get_chapter_schema,
    get_document_generation_prompt,
    get_document_response_schema,
    get_system_instruction,
    validate_document_structure,
)

# Provider factory
from src.services.ai.provider import (
    AIClientProtocol,
    AIProvider,
    AIProviderSettings,
    get_ai_client,
    get_ai_error_classes,
    get_provider_settings,
)

__all__ = [
    # Provider factory (recommended)
    "AIProvider",
    "AIClientProtocol",
    "AIProviderSettings",
    "get_ai_client",
    "get_provider_settings",
    "get_ai_error_classes",
    # Gemini
    "GeminiClient",
    "GeminiSettings",
    "GeminiError",
    "GeminiAPIError",
    "GeminiRateLimitError",
    "GeminiTimeoutError",
    "GeminiContentBlockedError",
    "GeminiInvalidResponseError",
    "get_gemini_client",
    "get_gemini_settings",
    # OpenRouter
    "OpenRouterClient",
    "OpenRouterSettings",
    "OpenRouterError",
    "OpenRouterAPIError",
    "OpenRouterRateLimitError",
    "OpenRouterTimeoutError",
    "OpenRouterContentBlockedError",
    "OpenRouterInvalidResponseError",
    "get_openrouter_client",
    "get_openrouter_settings",
    # Prompts
    "DocumentPrompts",
    "FileInfo",
    "DOCUMENT_RESPONSE_SCHEMA",
    "EDUCATIONAL_SYSTEM_INSTRUCTION",
    "KOREAN_EDUCATIONAL_SYSTEM_INSTRUCTION",
    "get_document_generation_prompt",
    "get_system_instruction",
    "get_document_response_schema",
    "get_chapter_schema",
    "validate_document_structure",
    "estimate_token_count",
]
