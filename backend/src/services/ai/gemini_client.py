"""
Gemini API Client Wrapper - AI Code Learning Platform

This module provides a wrapper around the Google Gemini API for generating
educational content, including learning documents, practice problems, and Q&A.

Features:
- Async-compatible API calls with retry logic
- Exponential backoff for rate limiting and transient errors
- JSON mode support for structured output (7-chapter documents)
- Safety settings configured for educational content
- Comprehensive error handling and logging
- Request timeout management

Usage:
    from src.services.ai.gemini_client import GeminiClient, get_gemini_client

    # Using dependency injection
    async def generate_document(code: str):
        client = get_gemini_client()
        result = await client.generate_content(
            prompt="Explain this code...",
            system_instruction="You are an expert teacher...",
            response_mime_type="application/json"
        )
        return result

Reference: research.md §3 - LLM Integration for Content Generation
Task: T091 - Implement Gemini API client wrapper
"""

import asyncio
import json
import logging
from functools import lru_cache
from typing import Any, Literal

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.generativeai.types import (
    GenerateContentResponse,
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class GeminiSettings(BaseSettings):
    """
    Gemini API configuration settings loaded from environment variables.

    Environment Variables:
        GEMINI_API_KEY: Google Gemini API key (required)
        GEMINI_MODEL: Model to use (default: gemini-3-flash-preview)
        GEMINI_TIMEOUT: Request timeout in seconds (default: 180)
        GEMINI_MAX_RETRIES: Maximum retry attempts (default: 3)
        GEMINI_RETRY_DELAY: Initial retry delay in seconds (default: 1.0)
        GEMINI_RETRY_MULTIPLIER: Exponential backoff multiplier (default: 2.0)
        GEMINI_MAX_RETRY_DELAY: Maximum retry delay in seconds (default: 60.0)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    gemini_api_key: str = Field(
        ...,  # Required
        description="Google Gemini API key",
    )
    gemini_model: str = Field(
        default="gemini-3-flash-preview",
        description="Gemini model to use",
    )
    gemini_timeout: int = Field(
        default=180,
        ge=10,
        le=600,
        description="Request timeout in seconds",
    )

    # Retry Configuration
    gemini_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )
    gemini_retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Initial retry delay in seconds",
    )
    gemini_retry_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        le=5.0,
        description="Exponential backoff multiplier",
    )
    gemini_max_retry_delay: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum retry delay in seconds",
    )


class GeminiError(Exception):
    """Base exception for Gemini API errors."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class GeminiAPIError(GeminiError):
    """API-level error from Gemini service."""

    pass


class GeminiRateLimitError(GeminiError):
    """Rate limit exceeded error."""

    pass


class GeminiTimeoutError(GeminiError):
    """Request timeout error."""

    pass


class GeminiContentBlockedError(GeminiError):
    """Content was blocked by safety filters."""

    pass


class GeminiInvalidResponseError(GeminiError):
    """Invalid or malformed response from API."""

    pass


class GeminiClient:
    """
    Async-compatible wrapper for Google Gemini API.

    Provides methods for generating educational content with built-in
    retry logic, error handling, and safety settings appropriate for
    beginner-friendly content.

    Attributes:
        settings: GeminiSettings configuration
        model: Configured GenerativeModel instance

    Example:
        client = GeminiClient()
        result = await client.generate_content(
            prompt="Explain this Python code: print('Hello')",
            system_instruction="You are an expert programming teacher."
        )

    Security Notes:
        - API key loaded from environment (never hardcoded)
        - Safety settings block harmful content
        - All requests are logged for audit
    """

    def __init__(self, settings: GeminiSettings | None = None):
        """
        Initialize GeminiClient with configuration.

        Args:
            settings: Optional GeminiSettings instance.
                     If not provided, settings are loaded from environment.
        """
        self.settings = settings or get_gemini_settings()
        self._configure_api()
        self._model: genai.GenerativeModel | None = None

    def _configure_api(self) -> None:
        """Configure the Gemini API with API key."""
        genai.configure(api_key=self.settings.gemini_api_key)
        logger.info(f"Gemini API configured with model: {self.settings.gemini_model}")

    @property
    def model(self) -> genai.GenerativeModel:
        """
        Get or create the GenerativeModel instance.

        Uses lazy initialization to defer model creation until first use.
        """
        if self._model is None:
            self._model = genai.GenerativeModel(
                model_name=self.settings.gemini_model,
                safety_settings=self._get_safety_settings(),
            )
        return self._model

    def _get_safety_settings(self) -> dict[HarmCategory, HarmBlockThreshold]:
        """
        Get safety settings for educational content.

        Configured to block harmful content while allowing educational
        discussions about code concepts, security, and error handling.

        Returns:
            dict: Safety settings mapping harm categories to thresholds
        """
        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

    def _get_generation_config(
        self,
        temperature: float = 0.7,
        max_output_tokens: int | None = None,
        response_mime_type: str | None = None,
        response_schema: dict[str, Any] | None = None,
    ) -> GenerationConfig:
        """
        Create generation configuration.

        Args:
            temperature: Creativity level (0.0-1.0). Lower = more deterministic.
            max_output_tokens: Maximum tokens in response. None = model default.
            response_mime_type: MIME type for response (e.g., "application/json").
            response_schema: JSON schema for structured output.

        Returns:
            GenerationConfig: Configuration for content generation
        """
        config = {
            "temperature": temperature,
        }
        if max_output_tokens:
            config["max_output_tokens"] = max_output_tokens
        if response_mime_type:
            config["response_mime_type"] = response_mime_type
        if response_schema:
            config["response_schema"] = response_schema

        return GenerationConfig(**config)

    async def generate_content(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int | None = None,
        response_mime_type: Literal["text/plain", "application/json"] | None = None,
        response_schema: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> str:
        """
        Generate content using Gemini API with retry logic.

        Args:
            prompt: The user prompt/question
            system_instruction: Optional system instruction for context
            temperature: Creativity level (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            response_mime_type: MIME type for structured output
            response_schema: JSON schema for response validation
            timeout: Request timeout (overrides default)

        Returns:
            str: Generated content text

        Raises:
            GeminiAPIError: API error after all retries exhausted
            GeminiRateLimitError: Rate limit exceeded
            GeminiTimeoutError: Request timed out
            GeminiContentBlockedError: Content blocked by safety filters
            GeminiInvalidResponseError: Invalid response from API
        """
        timeout = timeout or self.settings.gemini_timeout
        generation_config = self._get_generation_config(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
            response_schema=response_schema,
        )

        # Create model with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=self.settings.gemini_model,
                safety_settings=self._get_safety_settings(),
                system_instruction=system_instruction,
            )
        else:
            model = self.model

        last_error: Exception | None = None
        delay = self.settings.gemini_retry_delay

        for attempt in range(self.settings.gemini_max_retries + 1):
            try:
                logger.debug(
                    f"Gemini API call attempt {attempt + 1}/{self.settings.gemini_max_retries + 1}"
                )

                # Run synchronous API call in thread pool
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        model.generate_content,
                        prompt,
                        generation_config=generation_config,
                    ),
                    timeout=timeout,
                )

                return self._extract_response_text(response)

            except TimeoutError as e:
                last_error = e
                logger.warning(
                    f"Gemini API timeout (attempt {attempt + 1}): {timeout}s exceeded"
                )
                if attempt < self.settings.gemini_max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(
                        delay * self.settings.gemini_retry_multiplier,
                        self.settings.gemini_max_retry_delay,
                    )

            except google_exceptions.ResourceExhausted as e:
                last_error = e
                logger.warning(
                    f"Gemini API rate limit (attempt {attempt + 1}): {str(e)}"
                )
                if attempt < self.settings.gemini_max_retries:
                    await self._wait_with_backoff(delay * 2, attempt)
                    delay = min(
                        delay * self.settings.gemini_retry_multiplier,
                        self.settings.gemini_max_retry_delay,
                    )

            except google_exceptions.InvalidArgument as e:
                logger.error(f"Gemini API invalid argument: {str(e)}")
                raise GeminiAPIError(f"Invalid request to Gemini API: {str(e)}", e)

            except google_exceptions.GoogleAPIError as e:
                last_error = e
                logger.warning(f"Gemini API error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.settings.gemini_max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(
                        delay * self.settings.gemini_retry_multiplier,
                        self.settings.gemini_max_retry_delay,
                    )

            except Exception as e:
                last_error = e
                logger.error(
                    f"Unexpected error in Gemini API call: {type(e).__name__}: {str(e)}"
                )
                if attempt < self.settings.gemini_max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(
                        delay * self.settings.gemini_retry_multiplier,
                        self.settings.gemini_max_retry_delay,
                    )

        # All retries exhausted
        if isinstance(last_error, asyncio.TimeoutError):
            raise GeminiTimeoutError(
                f"Gemini API request timed out after {self.settings.gemini_max_retries + 1} attempts",
                last_error,
            )
        if isinstance(last_error, google_exceptions.ResourceExhausted):
            raise GeminiRateLimitError(
                f"Gemini API rate limit exceeded after {self.settings.gemini_max_retries + 1} attempts",
                last_error,
            )

        raise GeminiAPIError(
            f"Gemini API call failed after {self.settings.gemini_max_retries + 1} attempts: {str(last_error)}",
            last_error,
        )

    async def generate_json(
        self,
        prompt: str,
        system_instruction: str | None = None,
        response_schema: dict[str, Any] | None = None,
        temperature: float = 0.5,
        max_output_tokens: int | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate structured JSON content.

        Convenience method for generating JSON responses with automatic parsing.

        Args:
            prompt: The user prompt/question
            system_instruction: Optional system instruction for context
            response_schema: JSON schema for response validation
            temperature: Creativity level (lower for more consistent JSON)
            max_output_tokens: Maximum tokens in response
            timeout: Request timeout

        Returns:
            dict: Parsed JSON response

        Raises:
            GeminiInvalidResponseError: If response is not valid JSON
            (Other exceptions from generate_content)
        """
        response = await self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
            timeout=timeout,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.debug(f"Raw response: {response[:500]}...")
            raise GeminiInvalidResponseError(
                f"Invalid JSON response from Gemini: {str(e)}", e
            )

    def _extract_response_text(self, response: GenerateContentResponse) -> str:
        """
        Extract text from Gemini response.

        Handles various response formats and checks for blocked content.

        Args:
            response: GenerateContentResponse from API

        Returns:
            str: Extracted text content

        Raises:
            GeminiContentBlockedError: If content was blocked
            GeminiInvalidResponseError: If response format is invalid
        """
        # Check for blocked content
        if hasattr(response, "prompt_feedback"):
            feedback = response.prompt_feedback
            if hasattr(feedback, "block_reason") and feedback.block_reason:
                raise GeminiContentBlockedError(
                    f"Content blocked by safety filter: {feedback.block_reason}"
                )

        # Extract text from candidates
        if not response.candidates:
            raise GeminiInvalidResponseError("No candidates in response")

        candidate = response.candidates[0]

        # Check for finish reason
        if hasattr(candidate, "finish_reason"):
            finish_reason = str(candidate.finish_reason)
            if "SAFETY" in finish_reason:
                raise GeminiContentBlockedError(
                    f"Content blocked due to safety: {finish_reason}"
                )

        # Extract text from parts
        if not hasattr(candidate, "content") or not candidate.content:
            raise GeminiInvalidResponseError("No content in candidate")

        if not candidate.content.parts:
            raise GeminiInvalidResponseError("No parts in content")

        text_parts = []
        for part in candidate.content.parts:
            if hasattr(part, "text"):
                text_parts.append(part.text)

        if not text_parts:
            raise GeminiInvalidResponseError("No text found in response parts")

        return "".join(text_parts)

    async def _wait_with_backoff(self, delay: float, attempt: int) -> None:
        """
        Wait with exponential backoff before retry.

        Args:
            delay: Base delay in seconds
            attempt: Current attempt number (for logging)
        """
        logger.info(f"Retrying in {delay:.1f}s (attempt {attempt + 1})...")
        await asyncio.sleep(delay)

    async def check_health(self) -> dict[str, Any]:
        """
        Check Gemini API health by making a simple request.

        Returns:
            dict: Health status with model info and latency

        Raises:
            GeminiAPIError: If health check fails
        """
        import time

        start = time.time()
        try:
            response = await self.generate_content(
                prompt="Respond with 'OK' only.",
                temperature=0.0,
                max_output_tokens=10,
                timeout=30,
            )
            latency = time.time() - start

            return {
                "status": "healthy",
                "model": self.settings.gemini_model,
                "latency_seconds": round(latency, 3),
                "response": response.strip(),
            }
        except Exception as e:
            latency = time.time() - start
            return {
                "status": "unhealthy",
                "model": self.settings.gemini_model,
                "latency_seconds": round(latency, 3),
                "error": str(e),
            }


@lru_cache
def get_gemini_settings() -> GeminiSettings:
    """
    Get cached Gemini settings instance.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance and consistency.

    Returns:
        GeminiSettings: Cached settings instance
    """
    return GeminiSettings()


def get_gemini_client() -> GeminiClient:
    """
    Get a GeminiClient instance.

    Creates a new client with cached settings.

    Returns:
        GeminiClient: Configured client instance
    """
    return GeminiClient(get_gemini_settings())
