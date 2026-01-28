"""
Password Hashing Utilities - AI Code Learning Platform

This module provides password hashing utilities for secure user authentication,
using bcrypt as the hashing algorithm.

Features:
- Environment-based configuration with validation
- Secure password hashing with bcrypt
- Timing-safe password verification
- Configurable cost factor (rounds)
- Support for unicode passwords

Usage:
    from src.utils.security import (
        hash_password,
        verify_password,
        get_password_settings,
        PasswordHasher,
    )

    # Hash a password
    hashed = hash_password("user_password")

    # Verify a password
    is_valid = verify_password("user_password", hashed)

    # Using the class-based interface
    hasher = PasswordHasher()
    hashed = hasher.hash("user_password")
    is_valid = hasher.verify("user_password", hashed)
"""

from functools import lru_cache

import bcrypt
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PasswordSettings(BaseSettings):
    """
    Password hashing configuration settings loaded from environment variables.

    Environment Variables:
        BCRYPT_ROUNDS: Number of bcrypt rounds/cost factor (default: 12)

    Notes:
        - Higher rounds = more secure but slower
        - Minimum recommended: 10 for production
        - Default 12 provides good security/performance balance
        - bcrypt supports rounds 4-31
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bcrypt_rounds: int = Field(
        default=12,
        ge=4,  # bcrypt minimum
        le=31,  # bcrypt maximum
        description="Number of bcrypt rounds (cost factor)",
    )

    @field_validator("bcrypt_rounds")
    @classmethod
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """Validate bcrypt rounds are within acceptable range."""
        if v < 4:
            raise ValueError("bcrypt_rounds must be at least 4")
        if v > 31:
            raise ValueError("bcrypt_rounds must be at most 31")
        return v


class PasswordHashError(Exception):
    """Raised when password hashing fails."""

    pass


class PasswordVerifyError(Exception):
    """Raised when password verification encounters an error."""

    pass


@lru_cache
def get_password_settings() -> PasswordSettings:
    """
    Get cached password settings instance.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance and consistency.

    Returns:
        PasswordSettings: Cached settings instance
    """
    return PasswordSettings()


def hash_password(
    password: str,
    settings: PasswordSettings | None = None,
) -> str:
    """
    Hash a password using bcrypt.

    Creates a secure one-way hash of the password. Each call generates
    a unique hash due to random salt generation.

    Args:
        password: The plain-text password to hash
        settings: Optional PasswordSettings instance (uses cached default if not provided)

    Returns:
        str: The bcrypt hash string (60 characters)

    Raises:
        PasswordHashError: If the password is empty or hashing fails

    Example:
        hashed = hash_password("SecurePassword123!")
        # Returns: "$2b$12$..."

    Note:
        bcrypt has a 72-byte limit. Passwords longer than 72 bytes
        are automatically truncated (this is bcrypt's standard behavior).
    """
    if settings is None:
        settings = get_password_settings()

    if password is None:
        raise PasswordHashError("Password cannot be None")

    if len(password) == 0:
        raise PasswordHashError("Password cannot be empty")

    try:
        # Encode password to bytes (bcrypt works with bytes)
        password_bytes = password.encode("utf-8")

        # bcrypt has a 72-byte limit, truncate if necessary
        # This is standard bcrypt behavior - it would silently truncate anyway
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Generate salt with configured rounds
        salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)

        # Hash the password
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode("utf-8")
    except Exception as e:
        raise PasswordHashError(f"Failed to hash password: {e}") from e


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a password against a bcrypt hash.

    Uses timing-safe comparison to prevent timing attacks.
    Returns False for empty passwords rather than raising an error.

    Args:
        plain_password: The plain-text password to verify
        hashed_password: The bcrypt hash to verify against

    Returns:
        bool: True if the password matches, False otherwise

    Raises:
        PasswordVerifyError: If the hash format is invalid

    Example:
        is_valid = verify_password("SecurePassword123!", stored_hash)
        if is_valid:
            # Password is correct
    """
    if not plain_password:
        return False

    # Check for valid bcrypt hash format
    if not hashed_password or not hashed_password.startswith(("$2b$", "$2a$", "$2y$")):
        raise PasswordVerifyError("Invalid hash format: not a bcrypt hash")

    # Validate hash length (bcrypt hashes are 60 characters)
    if len(hashed_password) != 60:
        raise PasswordVerifyError("Invalid hash format: incorrect length")

    try:
        # Encode strings to bytes
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")

        # bcrypt has a 72-byte limit, truncate if necessary
        # Must match truncation in hash_password
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # bcrypt.checkpw performs timing-safe comparison
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except ValueError as e:
        raise PasswordVerifyError(f"Invalid hash format: {e}") from e
    except Exception:
        # For other errors, return False
        return False


class PasswordHasher:
    """
    Class-based password hasher for dependency injection.

    Provides an object-oriented interface for password hashing,
    useful for testing and dependency injection patterns.

    Attributes:
        settings: The password settings used for hashing

    Example:
        hasher = PasswordHasher()
        hashed = hasher.hash("password")
        is_valid = hasher.verify("password", hashed)
    """

    def __init__(self, settings: PasswordSettings | None = None) -> None:
        """
        Initialize the password hasher.

        Args:
            settings: Optional PasswordSettings instance
        """
        self.settings = settings or get_password_settings()

    def hash(self, password: str) -> str:
        """
        Hash a password using the configured settings.

        Args:
            password: The plain-text password to hash

        Returns:
            str: The bcrypt hash string

        Raises:
            PasswordHashError: If the password is empty or hashing fails
        """
        return hash_password(password, settings=self.settings)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            plain_password: The plain-text password to verify
            hashed_password: The bcrypt hash to verify against

        Returns:
            bool: True if the password matches, False otherwise
        """
        if not plain_password:
            return False

        try:
            return verify_password(plain_password, hashed_password)
        except PasswordVerifyError:
            return False
