"""
Authentication API Endpoints - AI Code Learning Platform

This module provides REST API endpoints for user authentication including
registration, login, logout, token refresh, and current user retrieval.

Features:
- User registration with email/password
- Login with JWT token issuance via HTTPOnly cookies
- Logout with token revocation
- Token refresh with rotation
- Current user endpoint for authenticated users

Endpoints:
    POST /auth/register - Create new user account
    POST /auth/login - Authenticate and get tokens
    GET /auth/me - Get current authenticated user
    POST /auth/logout - Revoke tokens and clear cookies
    POST /auth/refresh - Rotate tokens

Reference: api-spec.yaml Authentication endpoints
Tasks: T028-T031 - Authentication endpoint implementation
"""

import os
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser
from src.api.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    UnauthorizedError,
)
from src.db.session import get_db
from src.models.user import User
from src.services.auth.token_service import TokenService
from src.services.auth.user_service import UserService
from src.utils.jwt import get_jwt_settings

# =============================================================================
# Pydantic Schemas
# =============================================================================


class RegisterRequest(BaseModel):
    """
    Request schema for user registration.

    Attributes:
        email: Valid email address for the new account
        password: Password (minimum 8 characters)
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["SecurePass123!"],
    )


class LoginRequest(BaseModel):
    """
    Request schema for user login.

    Attributes:
        email: Registered email address
        password: Account password
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="User's password",
        examples=["SecurePass123!"],
    )


class UserResponse(BaseModel):
    """
    Response schema for user data.

    Returns user information without sensitive fields like password.

    Attributes:
        id: User's unique identifier
        email: User's email address
        skill_level: User's self-reported skill level
        created_at: Account creation timestamp
    """

    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    skill_level: str = Field(..., description="User's skill level")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "skill_level": "Complete Beginner",
                    "created_at": "2025-01-20T10:30:00Z",
                }
            ]
        },
    }


# =============================================================================
# Cookie Configuration
# =============================================================================


def _is_secure_environment() -> bool:
    """
    Check if running in a secure (production) environment.

    Returns:
        bool: True if Secure flag should be set on cookies
    """
    app_env = os.getenv("APP_ENV", "development")
    return app_env in ("production", "staging")


def _get_cookie_settings() -> dict:
    """
    Get common cookie configuration settings.

    Returns:
        dict: Cookie settings with security flags
    """
    get_jwt_settings()
    secure = _is_secure_environment()

    return {
        "httponly": True,
        "secure": secure,
        "samesite": "none" if secure else "lax",
    }


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """
    Set authentication cookies on the response.

    Args:
        response: FastAPI Response object
        access_token: JWT access token
        refresh_token: JWT refresh token
    """
    jwt_settings = get_jwt_settings()
    cookie_settings = _get_cookie_settings()

    # Calculate max_age in seconds
    access_max_age = int(jwt_settings.access_token_lifetime.total_seconds())
    refresh_max_age = int(jwt_settings.refresh_token_lifetime.total_seconds())

    # Set access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        path="/",
        **cookie_settings,
    )

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        path="/api/v1/auth",  # Only send to auth endpoints
        **cookie_settings,
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies from the response.

    Args:
        response: FastAPI Response object
    """
    cookie_settings = _get_cookie_settings()

    response.delete_cookie(
        key="access_token",
        path="/",
        **cookie_settings,
    )
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        **cookie_settings,
    )


def _user_to_response(user: User) -> UserResponse:
    """
    Convert User model to UserResponse schema.

    Args:
        user: User model instance

    Returns:
        UserResponse: Serialized user data
    """
    return UserResponse(
        id=user.id,
        email=user.email,
        skill_level=user.skill_level,
        created_at=user.created_at,
    )


# =============================================================================
# Router Definition
# =============================================================================

router = APIRouter()


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input (email format, password requirements)"},
        409: {"description": "Email already exists"},
    },
)
async def register(
    request: RegisterRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user account.

    Creates a new user with the provided email and password,
    then automatically logs them in by setting auth cookies.

    Args:
        request: Registration data (email, password)
        response: FastAPI Response for setting cookies
        db: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        ValidationError: If email format or password is invalid
        AlreadyExistsError: If email is already registered
    """
    # Create user via UserService
    user_service = UserService(db)
    user = await user_service.register(
        email=request.email,
        password=request.password,
    )

    # Generate tokens for automatic login
    token_service = TokenService(db)
    access_token, refresh_token = await token_service.create_token_pair(user.id)

    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)

    return _user_to_response(user)


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return JWT tokens in HTTPOnly cookies",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Authenticate a user with email and password.

    Validates credentials and issues JWT tokens via HTTPOnly cookies
    on successful authentication.

    Args:
        request: Login credentials (email, password)
        response: FastAPI Response for setting cookies
        db: Database session

    Returns:
        UserResponse: Authenticated user information

    Raises:
        InvalidCredentialsError: If email or password is incorrect
    """
    # Authenticate user via UserService
    user_service = UserService(db)
    user = await user_service.login(
        email=request.email,
        password=request.password,
    )

    # Generate tokens
    token_service = TokenService(db)
    access_token, refresh_token = await token_service.create_token_pair(user.id)

    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)

    return _user_to_response(user)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the currently authenticated user's information",
    responses={
        200: {"description": "User information retrieved"},
        401: {"description": "Not authenticated"},
    },
)
async def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get the current authenticated user.

    Requires a valid access token (via cookie or Authorization header).

    Args:
        current_user: Authenticated user from dependency

    Returns:
        UserResponse: Current user information

    Raises:
        UnauthorizedError: If not authenticated
    """
    return _user_to_response(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Revoke refresh token and clear cookies",
    responses={
        204: {"description": "Logout successful"},
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    """
    Logout the current user.

    Revokes the refresh token in the database and clears all auth cookies.
    This endpoint does not require authentication - it clears cookies regardless.

    Args:
        response: FastAPI Response for clearing cookies
        db: Database session
        refresh_token: Refresh token from cookie (optional)
    """
    # Revoke the refresh token if provided
    if refresh_token:
        token_service = TokenService(db)
        await token_service.revoke_refresh_token(refresh_token)

    # Clear cookies regardless of token validity
    clear_auth_cookies(response)


@router.post(
    "/refresh",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token",
    responses={
        200: {"description": "Token refreshed"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> UserResponse:
    """
    Refresh authentication tokens.

    Uses the refresh token from cookies to issue a new token pair.
    The old refresh token is revoked and a new one is issued (token rotation).

    Args:
        response: FastAPI Response for setting new cookies
        db: Database session
        refresh_token: Refresh token from cookie

    Returns:
        UserResponse: User information

    Raises:
        UnauthorizedError: If refresh token is missing
        TokenExpiredError: If refresh token has expired
        TokenInvalidError: If refresh token is invalid or revoked
    """
    if not refresh_token:
        raise UnauthorizedError(detail="Refresh token required")

    # Rotate tokens
    token_service = TokenService(db)
    try:
        new_access_token, new_refresh_token = await token_service.rotate_tokens(
            refresh_token
        )
    except TokenExpiredError:
        clear_auth_cookies(response)
        raise
    except TokenInvalidError:
        clear_auth_cookies(response)
        raise

    # Get user from the new access token
    payload = token_service.verify_access_token(new_access_token)
    user_service = UserService(db)
    user = await user_service.get_by_id(UUID(payload.sub))

    if user is None:
        clear_auth_cookies(response)
        raise UnauthorizedError(detail="User not found")

    # Set new cookies
    set_auth_cookies(response, new_access_token, new_refresh_token)

    return _user_to_response(user)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "router",
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
]
