"""
JWT Token Utilities - AI Code Learning Platform

This module provides JWT (JSON Web Token) utilities for authentication,
including token generation, verification, and decoding.

Features:
- Environment-based configuration with validation
- Access token generation (short-lived, 15 minutes)
- Refresh token generation (long-lived, 7 days)
- Token verification with signature validation
- Token decoding with expiration checking
- Support for custom claims and token types

Usage:
    from backend.src.utils.jwt import (
        create_access_token,
        create_refresh_token,
        verify_token,
        decode_token,
        get_jwt_settings,
    )

    # Generate tokens
    access_token = create_access_token(user_id="uuid-string")
    refresh_token = create_refresh_token(user_id="uuid-string")

    # Verify and decode
    payload = verify_token(access_token)
    if payload:
        user_id = payload.sub
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import lru_cache
from typing import Any
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenType(str, Enum):
    """Types of JWT tokens used in the application."""

    ACCESS = "access"
    REFRESH = "refresh"


class JWTSettings(BaseSettings):
    """
    JWT configuration settings loaded from environment variables.

    All settings have sensible development defaults but should be
    explicitly configured in production environments.

    Environment Variables:
        JWT_SECRET_KEY: Secret key for signing tokens (REQUIRED in production)
        JWT_ALGORITHM: Algorithm for signing (default: HS256)
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Access token lifetime (default: 15)
        JWT_REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime (default: 7)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    jwt_secret_key: str = Field(
        default="your-jwt-secret-key-change-in-production",
        description="Secret key for signing JWT tokens",
        min_length=32,
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT signing",
    )
    jwt_access_token_expire_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,  # Max 24 hours
        description="Access token expiration time in minutes",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        le=30,  # Max 30 days
        description="Refresh token expiration time in days",
    )

    @property
    def access_token_lifetime(self) -> timedelta:
        """Get access token lifetime as timedelta."""
        return timedelta(minutes=self.jwt_access_token_expire_minutes)

    @property
    def refresh_token_lifetime(self) -> timedelta:
        """Get refresh token lifetime as timedelta."""
        return timedelta(days=self.jwt_refresh_token_expire_days)


class TokenPayload(BaseModel):
    """
    JWT token payload schema.

    This represents the decoded payload from a JWT token.
    """

    sub: str = Field(
        ...,
        description="Subject - typically the user ID",
    )
    type: TokenType = Field(
        ...,
        description="Token type (access or refresh)",
    )
    exp: datetime = Field(
        ...,
        description="Token expiration timestamp",
    )
    iat: datetime = Field(
        ...,
        description="Token issued at timestamp",
    )
    jti: str | None = Field(
        default=None,
        description="JWT ID - unique identifier for the token",
    )

    @property
    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now(timezone.utc) > self.exp

    @property
    def is_access_token(self) -> bool:
        """Check if this is an access token."""
        return self.type == TokenType.ACCESS

    @property
    def is_refresh_token(self) -> bool:
        """Check if this is a refresh token."""
        return self.type == TokenType.REFRESH


class TokenError(Exception):
    """Base exception for token-related errors."""

    pass


class TokenExpiredError(TokenError):
    """Raised when a token has expired."""

    pass


class TokenInvalidError(TokenError):
    """Raised when a token is invalid or cannot be decoded."""

    pass


@lru_cache
def get_jwt_settings() -> JWTSettings:
    """
    Get cached JWT settings instance.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance and consistency.

    Returns:
        JWTSettings: Cached settings instance
    """
    return JWTSettings()


def create_access_token(
    user_id: str | UUID,
    extra_claims: dict[str, Any] | None = None,
    settings: JWTSettings | None = None,
) -> str:
    """
    Create a short-lived access token for API authentication.

    Access tokens are used for authenticating API requests and should
    be stored securely (e.g., in memory or HTTP-only cookies).

    Args:
        user_id: The user's unique identifier (string or UUID)
        extra_claims: Optional additional claims to include in the token
        settings: Optional JWTSettings instance (uses cached default if not provided)

    Returns:
        str: Encoded JWT access token

    Example:
        token = create_access_token(user_id="123e4567-e89b-12d3-a456-426614174000")
    """
    return _create_token(
        user_id=user_id,
        token_type=TokenType.ACCESS,
        extra_claims=extra_claims,
        settings=settings,
    )


def create_refresh_token(
    user_id: str | UUID,
    jti: str | None = None,
    extra_claims: dict[str, Any] | None = None,
    settings: JWTSettings | None = None,
) -> str:
    """
    Create a long-lived refresh token for obtaining new access tokens.

    Refresh tokens should be stored securely (e.g., in HTTP-only cookies)
    and rotated on use. The token hash should be stored in the database
    for revocation support.

    Args:
        user_id: The user's unique identifier (string or UUID)
        jti: Optional unique token identifier (for database tracking)
        extra_claims: Optional additional claims to include in the token
        settings: Optional JWTSettings instance (uses cached default if not provided)

    Returns:
        str: Encoded JWT refresh token

    Example:
        token = create_refresh_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            jti="unique-token-id"
        )
    """
    claims = extra_claims.copy() if extra_claims else {}
    if jti:
        claims["jti"] = jti

    return _create_token(
        user_id=user_id,
        token_type=TokenType.REFRESH,
        extra_claims=claims,
        settings=settings,
    )


def _create_token(
    user_id: str | UUID,
    token_type: TokenType,
    extra_claims: dict[str, Any] | None = None,
    settings: JWTSettings | None = None,
) -> str:
    """
    Internal function to create a JWT token.

    Args:
        user_id: The user's unique identifier
        token_type: Type of token (access or refresh)
        extra_claims: Optional additional claims
        settings: Optional JWTSettings instance

    Returns:
        str: Encoded JWT token
    """
    if settings is None:
        settings = get_jwt_settings()

    now = datetime.now(timezone.utc)

    # Determine expiration based on token type
    if token_type == TokenType.ACCESS:
        expires_delta = settings.access_token_lifetime
    else:
        expires_delta = settings.refresh_token_lifetime

    expire = now + expires_delta

    # Build payload
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": token_type.value,
        "iat": now,
        "exp": expire,
    }

    # Add extra claims if provided
    if extra_claims:
        payload.update(extra_claims)

    # Encode and return token
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(
    token: str,
    expected_type: TokenType | None = None,
    settings: JWTSettings | None = None,
) -> TokenPayload:
    """
    Verify a JWT token and return its decoded payload.

    This function validates the token signature, checks expiration,
    and optionally validates the token type.

    Args:
        token: The JWT token string to verify
        expected_type: Optional expected token type for validation
        settings: Optional JWTSettings instance

    Returns:
        TokenPayload: The decoded and validated token payload

    Raises:
        TokenExpiredError: If the token has expired
        TokenInvalidError: If the token is invalid, has wrong type, or cannot be decoded

    Example:
        try:
            payload = verify_token(token, expected_type=TokenType.ACCESS)
            user_id = payload.sub
        except TokenExpiredError:
            # Handle expired token
        except TokenInvalidError:
            # Handle invalid token
    """
    if settings is None:
        settings = get_jwt_settings()

    try:
        # Decode token with signature verification
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        # Convert timestamps to datetime
        payload["iat"] = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Parse token type
        payload["type"] = TokenType(payload["type"])

        # Create and validate payload
        token_payload = TokenPayload(**payload)

        # Validate token type if expected type is specified
        if expected_type is not None and token_payload.type != expected_type:
            raise TokenInvalidError(
                f"Invalid token type: expected {expected_type.value}, "
                f"got {token_payload.type.value}"
            )

        return token_payload

    except ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired") from e
    except JWTError as e:
        raise TokenInvalidError(f"Invalid token: {str(e)}") from e
    except (ValueError, KeyError) as e:
        raise TokenInvalidError(f"Malformed token payload: {str(e)}") from e


def decode_token(
    token: str,
    verify_signature: bool = True,
    settings: JWTSettings | None = None,
) -> TokenPayload:
    """
    Decode a JWT token without verifying expiration.

    This is useful for extracting claims from expired tokens
    (e.g., for logging or token refresh operations).

    Args:
        token: The JWT token string to decode
        verify_signature: Whether to verify the signature (default: True)
        settings: Optional JWTSettings instance

    Returns:
        TokenPayload: The decoded token payload

    Raises:
        TokenInvalidError: If the token cannot be decoded

    Example:
        # Decode expired token to get user_id for refresh
        payload = decode_token(token)
        user_id = payload.sub
    """
    if settings is None:
        settings = get_jwt_settings()

    options = {
        "verify_exp": False,  # Don't verify expiration
        "verify_signature": verify_signature,
    }

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options=options,
        )

        # Convert timestamps to datetime
        payload["iat"] = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Parse token type
        payload["type"] = TokenType(payload["type"])

        return TokenPayload(**payload)

    except JWTError as e:
        raise TokenInvalidError(f"Invalid token: {str(e)}") from e
    except (ValueError, KeyError) as e:
        raise TokenInvalidError(f"Malformed token payload: {str(e)}") from e


def get_token_expiration(token: str, settings: JWTSettings | None = None) -> datetime:
    """
    Get the expiration datetime of a token without full verification.

    Args:
        token: The JWT token string
        settings: Optional JWTSettings instance

    Returns:
        datetime: The token's expiration datetime

    Raises:
        TokenInvalidError: If the token cannot be decoded
    """
    payload = decode_token(token, verify_signature=False, settings=settings)
    return payload.exp


def is_token_expired(token: str, settings: JWTSettings | None = None) -> bool:
    """
    Check if a token has expired.

    Args:
        token: The JWT token string
        settings: Optional JWTSettings instance

    Returns:
        bool: True if the token has expired, False otherwise

    Raises:
        TokenInvalidError: If the token cannot be decoded
    """
    payload = decode_token(token, verify_signature=False, settings=settings)
    return payload.is_expired


def get_remaining_lifetime(token: str, settings: JWTSettings | None = None) -> timedelta:
    """
    Get the remaining lifetime of a token.

    Args:
        token: The JWT token string
        settings: Optional JWTSettings instance

    Returns:
        timedelta: Remaining time until expiration (negative if expired)

    Raises:
        TokenInvalidError: If the token cannot be decoded
    """
    payload = decode_token(token, verify_signature=False, settings=settings)
    return payload.exp - datetime.now(timezone.utc)
