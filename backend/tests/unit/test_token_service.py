"""
Unit Tests for TokenService - AI Code Learning Platform

Tests for the TokenService which handles:
- Access token creation and verification
- Refresh token creation with database storage
- Token rotation (issue new, revoke old)
- Token revocation (logout support)

Reference: data-model.md §RefreshToken entity
Task: T026 - Implement TokenService
TDD Phase: RED
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import TokenExpiredError, TokenInvalidError
from src.models.refresh_token import RefreshToken
from src.services.auth.token_service import TokenService
from src.utils.jwt import TokenType


class TestTokenServiceAccessToken:
    """Test access token creation and verification."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def token_service(self, mock_db: AsyncMock) -> TokenService:
        """Create TokenService instance with mocked database."""
        return TokenService(mock_db)

    def test_create_access_token_returns_string(
        self, token_service: TokenService
    ) -> None:
        """Access token should be returned as a string."""
        user_id = uuid.uuid4()
        token = token_service.create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_is_valid_jwt(
        self, token_service: TokenService
    ) -> None:
        """Access token should be a valid JWT with correct claims."""
        user_id = uuid.uuid4()
        token = token_service.create_access_token(user_id)

        # Verify token can be decoded
        payload = token_service.verify_access_token(token)
        assert payload.sub == str(user_id)
        assert payload.type == TokenType.ACCESS

    def test_create_access_token_with_extra_claims(
        self, token_service: TokenService
    ) -> None:
        """Access token should support extra claims."""
        user_id = uuid.uuid4()
        extra = {"role": "admin"}
        token = token_service.create_access_token(user_id, extra_claims=extra)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_access_token_returns_payload(
        self, token_service: TokenService
    ) -> None:
        """Valid access token should return TokenPayload."""
        user_id = uuid.uuid4()
        token = token_service.create_access_token(user_id)

        payload = token_service.verify_access_token(token)

        assert payload is not None
        assert payload.sub == str(user_id)
        assert payload.type == TokenType.ACCESS
        assert payload.exp > datetime.now(timezone.utc)

    def test_verify_access_token_rejects_refresh_token(
        self, token_service: TokenService
    ) -> None:
        """Verify should reject refresh tokens when access is expected."""
        from src.utils.jwt import create_refresh_token

        user_id = uuid.uuid4()
        refresh_token = create_refresh_token(user_id)

        with pytest.raises(TokenInvalidError):
            token_service.verify_access_token(refresh_token)

    def test_verify_access_token_rejects_invalid_token(
        self, token_service: TokenService
    ) -> None:
        """Verify should reject invalid tokens."""
        with pytest.raises(TokenInvalidError):
            token_service.verify_access_token("invalid.token.here")

    def test_verify_access_token_rejects_expired_token(
        self, token_service: TokenService
    ) -> None:
        """Verify should reject expired tokens."""
        from jose import jwt as jose_jwt
        from src.utils.jwt import get_jwt_settings

        user_id = uuid.uuid4()
        settings = get_jwt_settings()

        # Create an expired token by setting exp in the past
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

        with pytest.raises(TokenExpiredError):
            token_service.verify_access_token(expired_token)


class TestTokenServiceRefreshToken:
    """Test refresh token creation with database storage."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def token_service(self, mock_db: AsyncMock) -> TokenService:
        """Create TokenService instance with mocked database."""
        return TokenService(mock_db)

    @pytest.mark.asyncio
    async def test_create_refresh_token_returns_string(
        self, token_service: TokenService
    ) -> None:
        """Refresh token should be returned as a string."""
        user_id = uuid.uuid4()
        token = await token_service.create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_create_refresh_token_stores_hash_in_database(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Refresh token hash should be stored in database."""
        user_id = uuid.uuid4()
        token = await token_service.create_refresh_token(user_id)

        # Verify add was called with RefreshToken
        mock_db.add.assert_called_once()
        added_token = mock_db.add.call_args[0][0]
        assert isinstance(added_token, RefreshToken)
        assert added_token.user_id == user_id
        assert added_token.token_hash is not None
        assert not added_token.revoked

        # Verify commit was called
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_refresh_token_stores_sha256_hash(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Token hash should be SHA-256 of the raw token."""
        user_id = uuid.uuid4()
        token = await token_service.create_refresh_token(user_id)

        # Compute expected hash
        expected_hash = hashlib.sha256(token.encode()).hexdigest()

        # Get stored token
        added_token = mock_db.add.call_args[0][0]
        assert added_token.token_hash == expected_hash

    @pytest.mark.asyncio
    async def test_create_refresh_token_sets_expiration(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Refresh token should have expiration set (7 days by default)."""
        user_id = uuid.uuid4()
        await token_service.create_refresh_token(user_id)

        added_token = mock_db.add.call_args[0][0]
        assert added_token.expires_at is not None
        # Should expire in approximately 7 days (6-7 days to allow for timing)
        time_diff = added_token.expires_at - datetime.now(timezone.utc)
        # Check total seconds is between 6 and 7 days
        assert timedelta(days=6).total_seconds() < time_diff.total_seconds() <= timedelta(days=7).total_seconds()

    @pytest.mark.asyncio
    async def test_create_refresh_token_is_valid_jwt(
        self, token_service: TokenService
    ) -> None:
        """Refresh token should be a valid JWT with correct claims."""
        from src.utils.jwt import decode_token

        user_id = uuid.uuid4()
        token = await token_service.create_refresh_token(user_id)

        payload = decode_token(token)
        assert payload.sub == str(user_id)
        assert payload.type == TokenType.REFRESH
        assert payload.jti is not None  # Should have unique ID


class TestTokenServiceVerifyRefreshToken:
    """Test refresh token verification with database check."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def token_service(self, mock_db: AsyncMock) -> TokenService:
        """Create TokenService instance with mocked database."""
        return TokenService(mock_db)

    @pytest.mark.asyncio
    async def test_verify_refresh_token_returns_payload(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Valid refresh token should return payload."""
        user_id = uuid.uuid4()

        # Create token
        token = await token_service.create_refresh_token(user_id)
        stored_token = mock_db.add.call_args[0][0]

        # Mock database query to return the stored token
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = stored_token
        mock_db.execute.return_value = mock_result

        payload = await token_service.verify_refresh_token(token)

        assert payload is not None
        assert payload.sub == str(user_id)
        assert payload.type == TokenType.REFRESH

    @pytest.mark.asyncio
    async def test_verify_refresh_token_rejects_revoked_token(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Revoked refresh token should be rejected."""
        user_id = uuid.uuid4()

        # Create token
        token = await token_service.create_refresh_token(user_id)
        stored_token = mock_db.add.call_args[0][0]
        stored_token.revoked = True  # Mark as revoked

        # Mock database query to return the revoked token
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = stored_token
        mock_db.execute.return_value = mock_result

        with pytest.raises(TokenInvalidError):
            await token_service.verify_refresh_token(token)

    @pytest.mark.asyncio
    async def test_verify_refresh_token_rejects_unknown_token(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Unknown refresh token (not in database) should be rejected."""
        from src.utils.jwt import create_refresh_token

        # Create a valid JWT that's not in the database
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id, jti=str(uuid.uuid4()))

        # Mock database query to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(TokenInvalidError):
            await token_service.verify_refresh_token(token)

    @pytest.mark.asyncio
    async def test_verify_refresh_token_rejects_access_token(
        self, token_service: TokenService
    ) -> None:
        """Access token should be rejected when refresh is expected."""
        user_id = uuid.uuid4()
        access_token = token_service.create_access_token(user_id)

        with pytest.raises(TokenInvalidError):
            await token_service.verify_refresh_token(access_token)


class TestTokenServiceRotation:
    """Test token rotation (issue new, revoke old)."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def token_service(self, mock_db: AsyncMock) -> TokenService:
        """Create TokenService instance with mocked database."""
        return TokenService(mock_db)

    @pytest.mark.asyncio
    async def test_rotate_tokens_returns_new_token_pair(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Token rotation should return new access and refresh tokens."""
        user_id = uuid.uuid4()

        # Create initial refresh token
        old_refresh = await token_service.create_refresh_token(user_id)
        stored_token = mock_db.add.call_args[0][0]
        stored_token.user_id = user_id

        # Mock database query to return the stored token
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = stored_token
        mock_db.execute.return_value = mock_result

        # Rotate tokens
        mock_db.add.reset_mock()
        new_access, new_refresh = await token_service.rotate_tokens(old_refresh)

        assert isinstance(new_access, str)
        assert isinstance(new_refresh, str)
        assert new_refresh != old_refresh

    @pytest.mark.asyncio
    async def test_rotate_tokens_revokes_old_refresh_token(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Token rotation should revoke the old refresh token."""
        user_id = uuid.uuid4()

        # Create initial refresh token
        old_refresh = await token_service.create_refresh_token(user_id)
        stored_token = mock_db.add.call_args[0][0]
        stored_token.user_id = user_id

        # Mock database query to return the stored token
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = stored_token
        mock_db.execute.return_value = mock_result

        # Rotate tokens
        await token_service.rotate_tokens(old_refresh)

        # Old token should be marked as revoked
        assert stored_token.revoked is True
        assert stored_token.revoked_at is not None

    @pytest.mark.asyncio
    async def test_rotate_tokens_creates_new_refresh_in_database(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Token rotation should store new refresh token in database."""
        user_id = uuid.uuid4()

        # Create initial refresh token
        old_refresh = await token_service.create_refresh_token(user_id)
        stored_token = mock_db.add.call_args[0][0]
        stored_token.user_id = user_id
        old_hash = stored_token.token_hash

        # Mock database query to return the stored token
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = stored_token
        mock_db.execute.return_value = mock_result

        # Reset add mock to track new additions
        mock_db.add.reset_mock()

        # Rotate tokens
        await token_service.rotate_tokens(old_refresh)

        # New token should be added to database
        mock_db.add.assert_called()
        new_stored_token = mock_db.add.call_args[0][0]
        assert isinstance(new_stored_token, RefreshToken)
        assert new_stored_token.token_hash != old_hash


class TestTokenServiceRevocation:
    """Test token revocation for logout support."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def token_service(self, mock_db: AsyncMock) -> TokenService:
        """Create TokenService instance with mocked database."""
        return TokenService(mock_db)

    @pytest.mark.asyncio
    async def test_revoke_refresh_token_marks_as_revoked(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Revoke should mark token as revoked."""
        user_id = uuid.uuid4()

        # Create refresh token
        token = await token_service.create_refresh_token(user_id)
        stored_token = mock_db.add.call_args[0][0]

        # Mock database query to return the stored token
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = stored_token
        mock_db.execute.return_value = mock_result

        # Revoke token
        await token_service.revoke_refresh_token(token)

        assert stored_token.revoked is True
        assert stored_token.revoked_at is not None
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_revoke_refresh_token_handles_unknown_token(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Revoke should handle unknown token gracefully."""
        from src.utils.jwt import create_refresh_token

        # Create token not in database
        token = create_refresh_token(uuid.uuid4(), jti=str(uuid.uuid4()))

        # Mock database query to return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Should not raise, just return False or None
        result = await token_service.revoke_refresh_token(token)
        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Revoke all should mark all user tokens as revoked."""
        user_id = uuid.uuid4()

        # Mock database execute for update
        mock_db.execute.return_value = MagicMock()

        # Revoke all user tokens
        await token_service.revoke_all_user_tokens(user_id)

        # Should execute update and commit
        mock_db.execute.assert_called()
        mock_db.commit.assert_called()


class TestTokenServiceTokenPair:
    """Test creating token pairs (access + refresh)."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db

    @pytest.fixture
    def token_service(self, mock_db: AsyncMock) -> TokenService:
        """Create TokenService instance with mocked database."""
        return TokenService(mock_db)

    @pytest.mark.asyncio
    async def test_create_token_pair_returns_both_tokens(
        self, token_service: TokenService
    ) -> None:
        """Create token pair should return both access and refresh tokens."""
        user_id = uuid.uuid4()
        access_token, refresh_token = await token_service.create_token_pair(user_id)

        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert len(access_token) > 0
        assert len(refresh_token) > 0

    @pytest.mark.asyncio
    async def test_create_token_pair_access_token_is_valid(
        self, token_service: TokenService
    ) -> None:
        """Access token from pair should be valid."""
        user_id = uuid.uuid4()
        access_token, _ = await token_service.create_token_pair(user_id)

        payload = token_service.verify_access_token(access_token)
        assert payload.sub == str(user_id)
        assert payload.type == TokenType.ACCESS

    @pytest.mark.asyncio
    async def test_create_token_pair_refresh_token_stored(
        self, token_service: TokenService, mock_db: AsyncMock
    ) -> None:
        """Refresh token from pair should be stored in database."""
        user_id = uuid.uuid4()
        _, refresh_token = await token_service.create_token_pair(user_id)

        # Verify add was called
        mock_db.add.assert_called()
        added_token = mock_db.add.call_args[0][0]
        assert isinstance(added_token, RefreshToken)
        assert added_token.user_id == user_id
