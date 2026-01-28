"""
Unit Tests for Authentication Dependencies - AI Code Learning Platform

Tests for FastAPI dependencies that handle:
- Token extraction from Authorization header
- Access token verification
- Current user retrieval from database
- Optional authentication (for mixed-auth endpoints)

Reference: api-spec.yaml §Security (BearerAuth)
Task: T027 - Create authentication dependency for route protection
TDD Phase: RED
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import TokenExpiredError, TokenInvalidError, UnauthorizedError
from src.models.user import User


class TestGetCurrentUser:
    """Test get_current_user dependency for protected routes."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        return db

    @pytest.fixture
    def test_user(self) -> User:
        """Create a test user."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            skill_level="Complete Beginner",
        )

    @pytest.mark.asyncio
    async def test_get_current_user_returns_user_with_valid_token(
        self, mock_db: AsyncMock, test_user: User
    ) -> None:
        """Valid access token should return the authenticated user."""
        from src.api.dependencies import get_current_user
        from src.services.auth.token_service import TokenService

        # Create a valid token
        token_service = TokenService(mock_db)
        token = token_service.create_access_token(test_user.id)

        # Mock database query to return the user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db.execute.return_value = mock_result

        # Get current user
        user = await get_current_user(token=token, db=mock_db)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_raises_on_invalid_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Invalid token should raise UnauthorizedError."""
        from src.api.dependencies import get_current_user

        with pytest.raises((UnauthorizedError, TokenInvalidError)):
            await get_current_user(token="invalid.token.here", db=mock_db)

    @pytest.mark.asyncio
    async def test_get_current_user_raises_on_expired_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Expired token should raise TokenExpiredError."""
        from jose import jwt as jose_jwt

        from src.api.dependencies import get_current_user
        from src.utils.jwt import get_jwt_settings

        user_id = uuid.uuid4()
        settings = get_jwt_settings()

        # Create an expired token
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),  # Expired 1 hour ago
        }
        expired_token = jose_jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        with pytest.raises((TokenExpiredError, UnauthorizedError)):
            await get_current_user(token=expired_token, db=mock_db)

    @pytest.mark.asyncio
    async def test_get_current_user_raises_when_user_not_found(
        self, mock_db: AsyncMock
    ) -> None:
        """Token for non-existent user should raise UnauthorizedError."""
        from src.api.dependencies import get_current_user
        from src.services.auth.token_service import TokenService

        user_id = uuid.uuid4()
        token_service = TokenService(mock_db)
        token = token_service.create_access_token(user_id)

        # Mock database query to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(UnauthorizedError):
            await get_current_user(token=token, db=mock_db)

    @pytest.mark.asyncio
    async def test_get_current_user_raises_on_missing_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Missing token should raise UnauthorizedError."""
        from src.api.dependencies import get_current_user

        with pytest.raises(UnauthorizedError):
            await get_current_user(token=None, db=mock_db)

    @pytest.mark.asyncio
    async def test_get_current_user_raises_on_empty_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Empty token should raise UnauthorizedError."""
        from src.api.dependencies import get_current_user

        with pytest.raises(UnauthorizedError):
            await get_current_user(token="", db=mock_db)


class TestGetCurrentUserOptional:
    """Test get_current_user_optional dependency for mixed-auth routes."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        return db

    @pytest.fixture
    def test_user(self) -> User:
        """Create a test user."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            skill_level="Complete Beginner",
        )

    @pytest.mark.asyncio
    async def test_get_current_user_optional_returns_user_with_valid_token(
        self, mock_db: AsyncMock, test_user: User
    ) -> None:
        """Valid token should return the authenticated user."""
        from src.api.dependencies import get_current_user_optional
        from src.services.auth.token_service import TokenService

        token_service = TokenService(mock_db)
        token = token_service.create_access_token(test_user.id)

        # Mock database query to return the user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db.execute.return_value = mock_result

        user = await get_current_user_optional(token=token, db=mock_db)

        assert user is not None
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_current_user_optional_returns_none_without_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Missing token should return None (not raise error)."""
        from src.api.dependencies import get_current_user_optional

        user = await get_current_user_optional(token=None, db=mock_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_returns_none_on_invalid_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Invalid token should return None (not raise error)."""
        from src.api.dependencies import get_current_user_optional

        user = await get_current_user_optional(token="invalid.token.here", db=mock_db)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_returns_none_on_expired_token(
        self, mock_db: AsyncMock
    ) -> None:
        """Expired token should return None (not raise error)."""
        from jose import jwt as jose_jwt

        from src.api.dependencies import get_current_user_optional
        from src.utils.jwt import get_jwt_settings

        user_id = uuid.uuid4()
        settings = get_jwt_settings()

        # Create an expired token
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        }
        expired_token = jose_jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        user = await get_current_user_optional(token=expired_token, db=mock_db)
        assert user is None


class TestOAuth2Scheme:
    """Test OAuth2 scheme configuration."""

    def test_oauth2_scheme_is_configured(self) -> None:
        """OAuth2 scheme should be properly configured."""
        from src.api.dependencies import oauth2_scheme

        assert oauth2_scheme is not None
        assert oauth2_scheme.auto_error is False  # We handle errors manually

    def test_oauth2_scheme_token_url(self) -> None:
        """OAuth2 scheme should have correct token URL."""
        from src.api.dependencies import oauth2_scheme

        # Token URL should point to login endpoint
        assert "auth/login" in oauth2_scheme.model.flows.password.tokenUrl


class TestRequireAuth:
    """Test require_auth dependency wrapper."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def test_user(self) -> User:
        """Create a test user."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash="hashed_password",
            skill_level="Complete Beginner",
        )

    @pytest.mark.asyncio
    async def test_require_auth_returns_user_with_valid_token(
        self, mock_db: AsyncMock, test_user: User
    ) -> None:
        """Valid token should return the authenticated user."""
        from src.api.dependencies import require_auth
        from src.services.auth.token_service import TokenService

        token_service = TokenService(mock_db)
        token = token_service.create_access_token(test_user.id)

        # Mock database query to return the user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db.execute.return_value = mock_result

        user = await require_auth(token=token, db=mock_db)

        assert user is not None
        assert user.id == test_user.id
