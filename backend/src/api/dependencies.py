"""
Authentication Dependencies - AI Code Learning Platform

This module provides FastAPI dependencies for route protection and
user authentication using JWT tokens.

Features:
- OAuth2 Bearer token extraction from Authorization header
- Access token verification with TokenService
- Current user retrieval from database
- Optional authentication for mixed-auth endpoints
- Standard FastAPI dependency injection pattern

Usage:
    from src.api.dependencies import get_current_user, require_auth

    # Protected endpoint (requires authentication)
    @app.get("/protected")
    async def protected_route(
        current_user: User = Depends(require_auth)
    ):
        return {"user_id": current_user.id}

    # Mixed endpoint (optional authentication)
    @app.get("/public")
    async def public_route(
        current_user: User | None = Depends(get_current_user_optional)
    ):
        if current_user:
            return {"message": f"Hello, {current_user.email}"}
        return {"message": "Hello, guest"}

Reference: api-spec.yaml §Security (BearerAuth)
Task: T027 - Create authentication dependency for route protection
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import TokenExpiredError, TokenInvalidError, UnauthorizedError
from src.db.session import get_db
from src.models.user import User
from src.services.auth.token_service import TokenService

# =============================================================================
# OAuth2 Scheme Configuration
# =============================================================================

# OAuth2 scheme for extracting Bearer tokens from Authorization header
# auto_error=False allows us to handle missing tokens manually for better error messages
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,  # Don't auto-raise HTTPException, we handle it
    scheme_name="BearerAuth",
    description="JWT Bearer token authentication",
)


# =============================================================================
# Authentication Dependencies
# =============================================================================


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    FastAPI dependency that extracts and validates the current user.

    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. If not found, extracts from access_token cookie (for browser clients)
    3. Verifies the access token using TokenService
    4. Retrieves the user from the database
    5. Raises appropriate errors for invalid/missing tokens

    Args:
        request: FastAPI Request object for cookie access
        token: JWT access token extracted by OAuth2PasswordBearer
        db: Database session from get_db dependency

    Returns:
        User: The authenticated user instance

    Raises:
        UnauthorizedError: If token is missing, invalid, or user not found
        TokenExpiredError: If the token has expired

    Usage:
        @app.get("/me")
        async def get_me(user: User = Depends(get_current_user)):
            return {"email": user.email}
    """
    # Check if token is provided in Authorization header
    # If not, try to get it from access_token cookie (browser clients)
    if not token:
        token = request.cookies.get("access_token")

    # Still no token found - authentication required
    if not token:
        raise UnauthorizedError(detail="Authentication required")

    # Verify the access token
    token_service = TokenService(db)
    try:
        payload = token_service.verify_access_token(token)
    except TokenExpiredError:
        # Re-raise TokenExpiredError as-is for specific handling
        raise TokenExpiredError(detail="Access token has expired")
    except TokenInvalidError:
        raise UnauthorizedError(detail="Invalid access token")

    # Extract user ID from token payload
    try:
        user_id = UUID(payload.sub)
    except ValueError:
        raise UnauthorizedError(detail="Invalid token payload")

    # Retrieve user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError(detail="User not found")

    return user


async def get_current_user_optional(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    FastAPI dependency that optionally extracts the current user.

    Similar to get_current_user but returns None instead of raising
    errors when authentication fails. Useful for endpoints that
    work both with and without authentication.

    Args:
        request: FastAPI Request object for cookie access
        token: JWT access token extracted by OAuth2PasswordBearer
        db: Database session from get_db dependency

    Returns:
        User | None: The authenticated user or None if not authenticated

    Usage:
        @app.get("/content")
        async def get_content(
            user: User | None = Depends(get_current_user_optional)
        ):
            if user:
                return {"personalized": True, "user_id": user.id}
            return {"personalized": False}
    """
    # Check for token in header or cookie
    if not token:
        token = request.cookies.get("access_token")

    # No token provided - return None silently
    if not token:
        return None

    try:
        # Try to get the user using the standard dependency
        return await get_current_user(request=request, token=token, db=db)
    except (UnauthorizedError, TokenExpiredError, TokenInvalidError):
        # Any auth failure returns None for optional auth
        return None


# Alias for explicit semantics in protected routes
async def require_auth(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Explicit dependency for routes that require authentication.

    This is an alias for get_current_user with clearer semantic naming.
    Use this to make route protection intent explicit in code.

    Args:
        request: FastAPI Request object for cookie access
        token: JWT access token extracted by OAuth2PasswordBearer
        db: Database session from get_db dependency

    Returns:
        User: The authenticated user instance

    Raises:
        UnauthorizedError: If authentication fails

    Usage:
        @app.post("/projects")
        async def create_project(
            current_user: User = Depends(require_auth)
        ):
            # Only authenticated users can create projects
            ...
    """
    return await get_current_user(request=request, token=token, db=db)


# =============================================================================
# Type Annotations for Dependency Injection
# =============================================================================

# Annotated types for cleaner dependency injection syntax
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
RequiredUser = Annotated[User, Depends(require_auth)]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # OAuth2 scheme
    "oauth2_scheme",
    # Dependencies
    "get_current_user",
    "get_current_user_optional",
    "require_auth",
    # Type annotations
    "CurrentUser",
    "OptionalUser",
    "RequiredUser",
]
