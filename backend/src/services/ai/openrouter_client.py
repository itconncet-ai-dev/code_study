"""
OpenRouter API Client Wrapper - AI Code Learning Platform

This module provides a wrapper around the OpenRouter API for generating
educational content using various LLM models including gpt-oss-120b.

Features:
- Async-compatible API calls with retry logic
- Exponential backoff for rate limiting and transient errors
- JSON mode support for structured output (7-chapter documents)
- Compatible interface with GeminiClient for easy switching
- Comprehensive error handling and logging

Usage:
    from src.services.ai.openrouter_client import OpenRouterClient, get_openrouter_client

    client = get_openrouter_client()
    result = await client.generate_content(
        prompt="Explain this code...",
        system_instruction="You are an expert teacher..."
    )

Reference: https://openrouter.ai/docs/quickstart
"""

import asyncio
import json
import logging
from functools import lru_cache
from typing import Any, Literal

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class OpenRouterSettings(BaseSettings):
    """
    OpenRouter API configuration settings loaded from environment variables.

    Environment Variables:
        OPENROUTER_API_KEY: OpenRouter API key (required)
        OPENROUTER_MODEL: Model to use (default: openai/gpt-oss-120b:free)
        OPENROUTER_BASE_URL: API base URL (default: https://openrouter.ai/api/v1)
        OPENROUTER_TIMEOUT: Request timeout in seconds (default: 180)
        OPENROUTER_MAX_RETRIES: Maximum retry attempts (default: 3)
        OPENROUTER_RETRY_DELAY: Initial retry delay in seconds (default: 1.0)
        OPENROUTER_RETRY_MULTIPLIER: Exponential backoff multiplier (default: 2.0)
        OPENROUTER_MAX_RETRY_DELAY: Maximum retry delay in seconds (default: 60.0)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    openrouter_api_key: str = Field(
        ...,  # Required
        description="OpenRouter API key",
    )
    openrouter_model: str = Field(
        default="openai/gpt-oss-120b:free",
        description="OpenRouter model to use",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL",
    )
    openrouter_timeout: int = Field(
        default=180,
        ge=10,
        le=600,
        description="Request timeout in seconds",
    )

    # Retry Configuration
    openrouter_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )
    openrouter_retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Initial retry delay in seconds",
    )
    openrouter_retry_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        le=5.0,
        description="Exponential backoff multiplier",
    )
    openrouter_max_retry_delay: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum retry delay in seconds",
    )

    # Optional headers for OpenRouter
    openrouter_site_url: str = Field(
        default="",
        description="Your site URL for OpenRouter leaderboard",
    )
    openrouter_site_name: str = Field(
        default="AI Code Learning Platform",
        description="Your site name for OpenRouter leaderboard",
    )


class OpenRouterError(Exception):
    """Base exception for OpenRouter API errors."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class OpenRouterAPIError(OpenRouterError):
    """API-level error from OpenRouter service."""

    pass


class OpenRouterRateLimitError(OpenRouterError):
    """Rate limit exceeded error."""

    pass


class OpenRouterTimeoutError(OpenRouterError):
    """Request timeout error."""

    pass


class OpenRouterContentBlockedError(OpenRouterError):
    """Content was blocked by safety filters."""

    pass


class OpenRouterInvalidResponseError(OpenRouterError):
    """Invalid or malformed response from API."""

    pass


class OpenRouterClient:
    """
    Async-compatible wrapper for OpenRouter API.

    Provides methods for generating educational content with built-in
    retry logic, error handling, and compatibility with GeminiClient interface.

    Attributes:
        settings: OpenRouterSettings configuration

    Example:
        client = OpenRouterClient()
        result = await client.generate_content(
            prompt="Explain this Python code: print('Hello')",
            system_instruction="You are an expert programming teacher."
        )

    Security Notes:
        - API key loaded from environment (never hardcoded)
        - All requests are logged for audit
    """

    def __init__(self, settings: OpenRouterSettings | None = None):
        """
        Initialize OpenRouterClient with configuration.

        Args:
            settings: Optional OpenRouterSettings instance.
                     If not provided, settings are loaded from environment.
        """
        self.settings = settings or get_openrouter_settings()
        self._client: httpx.AsyncClient | None = None
        logger.info(
            f"OpenRouter client configured with model: {self.settings.openrouter_model}"
        )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers including authentication."""
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        if self.settings.openrouter_site_url:
            headers["HTTP-Referer"] = self.settings.openrouter_site_url
        if self.settings.openrouter_site_name:
            headers["X-Title"] = self.settings.openrouter_site_name
        return headers

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
        Generate content using OpenRouter API with retry logic.

        Args:
            prompt: The user prompt/question
            system_instruction: Optional system instruction for context
            temperature: Creativity level (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            response_mime_type: MIME type for structured output
            response_schema: JSON schema for response validation (used in prompt)
            timeout: Request timeout (overrides default)

        Returns:
            str: Generated content text

        Raises:
            OpenRouterAPIError: API error after all retries exhausted
            OpenRouterRateLimitError: Rate limit exceeded
            OpenRouterTimeoutError: Request timed out
            OpenRouterContentBlockedError: Content blocked by safety filters
            OpenRouterInvalidResponseError: Invalid response from API
        """
        timeout = timeout or self.settings.openrouter_timeout

        # Build messages
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        # If JSON mode is requested, add instruction to prompt
        user_content = prompt
        if response_mime_type == "application/json":
            if response_schema:
                user_content = f"{prompt}\n\nRespond with valid JSON matching this schema: {json.dumps(response_schema)}"
            else:
                user_content = f"{prompt}\n\nRespond with valid JSON only."

        messages.append({"role": "user", "content": user_content})

        # Build request body
        request_body: dict[str, Any] = {
            "model": self.settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_output_tokens:
            request_body["max_tokens"] = max_output_tokens

        if response_mime_type == "application/json":
            request_body["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        delay = self.settings.openrouter_retry_delay

        for attempt in range(self.settings.openrouter_max_retries + 1):
            try:
                logger.debug(
                    f"OpenRouter API call attempt {attempt + 1}/{self.settings.openrouter_max_retries + 1}"
                )

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        f"{self.settings.openrouter_base_url}/chat/completions",
                        headers=self._get_headers(),
                        json=request_body,
                    )

                # Check for HTTP errors
                if response.status_code == 429:
                    error_msg = response.text
                    logger.warning(
                        f"OpenRouter rate limit (attempt {attempt + 1}): {error_msg}"
                    )
                    last_error = OpenRouterRateLimitError(error_msg)
                    if attempt < self.settings.openrouter_max_retries:
                        await self._wait_with_backoff(delay * 2, attempt)
                        delay = min(
                            delay * self.settings.openrouter_retry_multiplier,
                            self.settings.openrouter_max_retry_delay,
                        )
                        continue
                    raise last_error

                if response.status_code >= 400:
                    error_msg = response.text
                    logger.warning(
                        f"OpenRouter API error (attempt {attempt + 1}): {response.status_code} - {error_msg}"
                    )
                    last_error = OpenRouterAPIError(
                        f"API error {response.status_code}: {error_msg}"
                    )
                    if attempt < self.settings.openrouter_max_retries:
                        await self._wait_with_backoff(delay, attempt)
                        delay = min(
                            delay * self.settings.openrouter_retry_multiplier,
                            self.settings.openrouter_max_retry_delay,
                        )
                        continue
                    raise last_error

                # Parse response
                data = response.json()
                return self._extract_response_text(data)

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    f"OpenRouter timeout (attempt {attempt + 1}): {timeout}s exceeded"
                )
                if attempt < self.settings.openrouter_max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(
                        delay * self.settings.openrouter_retry_multiplier,
                        self.settings.openrouter_max_retry_delay,
                    )

            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    f"OpenRouter request error (attempt {attempt + 1}): {str(e)}"
                )
                if attempt < self.settings.openrouter_max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(
                        delay * self.settings.openrouter_retry_multiplier,
                        self.settings.openrouter_max_retry_delay,
                    )

            except (OpenRouterRateLimitError, OpenRouterAPIError):
                raise

            except Exception as e:
                last_error = e
                logger.error(
                    f"Unexpected error in OpenRouter API call: {type(e).__name__}: {str(e)}"
                )
                if attempt < self.settings.openrouter_max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(
                        delay * self.settings.openrouter_retry_multiplier,
                        self.settings.openrouter_max_retry_delay,
                    )

        # All retries exhausted
        if isinstance(last_error, httpx.TimeoutException):
            raise OpenRouterTimeoutError(
                f"OpenRouter API request timed out after {self.settings.openrouter_max_retries + 1} attempts",
                last_error,
            )

        raise OpenRouterAPIError(
            f"OpenRouter API call failed after {self.settings.openrouter_max_retries + 1} attempts: {str(last_error)}",
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
            OpenRouterInvalidResponseError: If response is not valid JSON
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
            logger.error(f"Failed to parse OpenRouter JSON response: {str(e)}")
            logger.debug(f"Raw response: {response[:500]}...")
            raise OpenRouterInvalidResponseError(
                f"Invalid JSON response from OpenRouter: {str(e)}", e
            )

    def _extract_response_text(self, data: dict[str, Any]) -> str:
        """
        Extract text from OpenRouter response.

        Args:
            data: Response JSON from API

        Returns:
            str: Extracted text content

        Raises:
            OpenRouterContentBlockedError: If content was blocked
            OpenRouterInvalidResponseError: If response format is invalid
        """
        # Check for error in response
        if "error" in data:
            error = data["error"]
            error_msg = error.get("message", str(error))
            if "content" in error_msg.lower() and "block" in error_msg.lower():
                raise OpenRouterContentBlockedError(f"Content blocked: {error_msg}")
            raise OpenRouterAPIError(f"API error: {error_msg}")

        # Extract from choices
        choices = data.get("choices", [])
        if not choices:
            raise OpenRouterInvalidResponseError("No choices in response")

        choice = choices[0]
        message = choice.get("message", {})
        content = message.get("content")

        if content is None:
            # Check finish reason
            finish_reason = choice.get("finish_reason", "")
            if finish_reason == "content_filter":
                raise OpenRouterContentBlockedError("Content blocked by content filter")
            raise OpenRouterInvalidResponseError("No content in response message")

        return content

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
        Check OpenRouter API health by making a simple request.

        Returns:
            dict: Health status with model info and latency

        Raises:
            OpenRouterAPIError: If health check fails
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
                "model": self.settings.openrouter_model,
                "latency_seconds": round(latency, 3),
                "response": response.strip(),
            }
        except Exception as e:
            latency = time.time() - start
            return {
                "status": "unhealthy",
                "model": self.settings.openrouter_model,
                "latency_seconds": round(latency, 3),
                "error": str(e),
            }


@lru_cache
def get_openrouter_settings() -> OpenRouterSettings:
    """
    Get cached OpenRouter settings instance.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance and consistency.

    Returns:
        OpenRouterSettings: Cached settings instance
    """
    return OpenRouterSettings()


def get_openrouter_client() -> OpenRouterClient:
    """
    Get an OpenRouterClient instance.

    Creates a new client with cached settings.

    Returns:
        OpenRouterClient: Configured client instance
    """
    return OpenRouterClient(get_openrouter_settings())
