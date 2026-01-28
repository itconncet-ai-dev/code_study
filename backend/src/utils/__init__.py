"""
Utils Package - Shared utilities and helper functions.

This package provides utility modules for:
- JWT token handling (jwt.py) - Token generation, verification, and decoding
- Security utilities (security.py) - Password hashing with bcrypt
"""

from src.utils.jwt import (
    JWTSettings,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenPayload,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_settings,
    get_remaining_lifetime,
    get_token_expiration,
    is_token_expired,
    verify_token,
)
from src.utils.security import (
    PasswordHasher,
    PasswordHashError,
    PasswordSettings,
    PasswordVerifyError,
    get_password_settings,
    hash_password,
    verify_password,
)
from src.utils.file_validator import (
    FileValidator,
    ValidationResult,
)

__all__ = [
    # JWT Settings
    "JWTSettings",
    "get_jwt_settings",
    # Token Types
    "TokenType",
    "TokenPayload",
    # Token Creation
    "create_access_token",
    "create_refresh_token",
    # Token Verification
    "verify_token",
    "decode_token",
    # Token Utilities
    "get_token_expiration",
    "is_token_expired",
    "get_remaining_lifetime",
    # JWT Exceptions
    "TokenError",
    "TokenExpiredError",
    "TokenInvalidError",
    # Password Settings
    "PasswordSettings",
    "get_password_settings",
    # Password Hashing
    "PasswordHasher",
    "hash_password",
    "verify_password",
    # Password Exceptions
    "PasswordHashError",
    "PasswordVerifyError",
    # File Validation
    "FileValidator",
    "ValidationResult",
]
