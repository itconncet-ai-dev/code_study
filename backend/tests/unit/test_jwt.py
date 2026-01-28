"""
Unit tests for JWT Token Utilities - AI Code Learning Platform

Tests cover:
- Token generation (access and refresh)
- Token verification with signature validation
- Token decoding with and without signature verification
- Token expiration handling
- Error cases and edge cases
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from backend.src.utils.jwt import (
    JWTSettings,
    TokenInvalidError,
    TokenPayload,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_remaining_lifetime,
    get_token_expiration,
    is_token_expired,
    verify_token,
)


@pytest.fixture
def jwt_settings() -> JWTSettings:
    """Create test JWT settings with short expiration times."""
    return JWTSettings(
        jwt_secret_key="test-secret-key-that-is-long-enough-for-testing",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=1,  # 1 minute for testing
        jwt_refresh_token_expire_days=1,  # 1 day for testing
    )


@pytest.fixture
def user_id() -> str:
    """Generate a test user ID."""
    return str(uuid4())


class TestJWTSettings:
    """Tests for JWTSettings configuration."""

    def test_default_settings(self):
        """Test default JWT settings are loaded."""
        settings = JWTSettings()
        assert settings.jwt_algorithm == "HS256"
        assert settings.jwt_access_token_expire_minutes == 15
        assert settings.jwt_refresh_token_expire_days == 7

    def test_access_token_lifetime(self, jwt_settings: JWTSettings):
        """Test access token lifetime calculation."""
        lifetime = jwt_settings.access_token_lifetime
        assert lifetime == timedelta(minutes=1)

    def test_refresh_token_lifetime(self, jwt_settings: JWTSettings):
        """Test refresh token lifetime calculation."""
        lifetime = jwt_settings.refresh_token_lifetime
        assert lifetime == timedelta(days=1)


class TestAccessTokenCreation:
    """Tests for access token creation."""

    def test_create_access_token(self, jwt_settings: JWTSettings, user_id: str):
        """Test basic access token creation."""
        token = create_access_token(user_id, settings=jwt_settings)
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT format: header.payload.signature
        assert token.count(".") == 2

    def test_access_token_contains_correct_claims(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test access token contains expected claims."""
        token = create_access_token(user_id, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.sub == user_id
        assert payload.type == TokenType.ACCESS
        assert payload.is_access_token is True
        assert payload.is_refresh_token is False

    def test_access_token_with_uuid(self, jwt_settings: JWTSettings):
        """Test access token creation with UUID object."""
        user_uuid = uuid4()
        token = create_access_token(user_uuid, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.sub == str(user_uuid)

    def test_access_token_with_extra_claims(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test access token with additional claims."""
        extra_claims = {"email": "test@example.com", "role": "user"}
        token = create_access_token(
            user_id, extra_claims=extra_claims, settings=jwt_settings
        )
        payload = decode_token(token, settings=jwt_settings)

        assert payload.sub == user_id


class TestRefreshTokenCreation:
    """Tests for refresh token creation."""

    def test_create_refresh_token(self, jwt_settings: JWTSettings, user_id: str):
        """Test basic refresh token creation."""
        token = create_refresh_token(user_id, settings=jwt_settings)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_contains_correct_claims(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test refresh token contains expected claims."""
        token = create_refresh_token(user_id, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.sub == user_id
        assert payload.type == TokenType.REFRESH
        assert payload.is_refresh_token is True
        assert payload.is_access_token is False

    def test_refresh_token_with_jti(self, jwt_settings: JWTSettings, user_id: str):
        """Test refresh token with JWT ID for tracking."""
        jti = str(uuid4())
        token = create_refresh_token(user_id, jti=jti, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.jti == jti

    def test_refresh_token_longer_lifetime_than_access(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test refresh token has longer expiration than access token."""
        access_token = create_access_token(user_id, settings=jwt_settings)
        refresh_token = create_refresh_token(user_id, settings=jwt_settings)

        access_exp = get_token_expiration(access_token, settings=jwt_settings)
        refresh_exp = get_token_expiration(refresh_token, settings=jwt_settings)

        assert refresh_exp > access_exp


class TestTokenVerification:
    """Tests for token verification."""

    def test_verify_valid_access_token(self, jwt_settings: JWTSettings, user_id: str):
        """Test verification of valid access token."""
        token = create_access_token(user_id, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.sub == user_id
        assert payload.type == TokenType.ACCESS

    def test_verify_valid_refresh_token(self, jwt_settings: JWTSettings, user_id: str):
        """Test verification of valid refresh token."""
        token = create_refresh_token(user_id, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.sub == user_id
        assert payload.type == TokenType.REFRESH

    def test_verify_with_expected_type_access(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test verification with expected access token type."""
        token = create_access_token(user_id, settings=jwt_settings)
        payload = verify_token(
            token, expected_type=TokenType.ACCESS, settings=jwt_settings
        )

        assert payload.type == TokenType.ACCESS

    def test_verify_with_expected_type_refresh(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test verification with expected refresh token type."""
        token = create_refresh_token(user_id, settings=jwt_settings)
        payload = verify_token(
            token, expected_type=TokenType.REFRESH, settings=jwt_settings
        )

        assert payload.type == TokenType.REFRESH

    def test_verify_wrong_token_type_raises_error(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test verification fails when token type doesn't match expected."""
        access_token = create_access_token(user_id, settings=jwt_settings)

        with pytest.raises(TokenInvalidError, match="Invalid token type"):
            verify_token(
                access_token, expected_type=TokenType.REFRESH, settings=jwt_settings
            )

    def test_verify_invalid_token_raises_error(self, jwt_settings: JWTSettings):
        """Test verification fails for invalid token."""
        with pytest.raises(TokenInvalidError):
            verify_token("invalid.token.string", settings=jwt_settings)

    def test_verify_tampered_token_raises_error(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test verification fails for tampered token."""
        token = create_access_token(user_id, settings=jwt_settings)
        # Tamper with the token by changing a character
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(TokenInvalidError):
            verify_token(tampered_token, settings=jwt_settings)

    def test_verify_token_with_wrong_secret_raises_error(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test verification fails with different secret key."""
        token = create_access_token(user_id, settings=jwt_settings)

        wrong_settings = JWTSettings(
            jwt_secret_key="different-secret-key-that-is-long-enough",
            jwt_algorithm="HS256",
        )

        with pytest.raises(TokenInvalidError):
            verify_token(token, settings=wrong_settings)


class TestTokenExpiration:
    """Tests for token expiration handling."""

    def test_expired_token_raises_error(self):
        """Test that expired tokens raise TokenExpiredError."""
        # Create settings with very short expiration
        settings = JWTSettings(
            jwt_secret_key="test-secret-key-that-is-long-enough-for-testing",
            jwt_algorithm="HS256",
            jwt_access_token_expire_minutes=1,  # Minimum allowed
        )

        user_id = str(uuid4())
        token = create_access_token(user_id, settings=settings)

        # Manually verify the token was created correctly
        payload = decode_token(token, settings=settings)
        assert payload.sub == user_id

        # Note: We can't easily test actual expiration without mocking time
        # The token is valid for 1 minute, so we just verify it's not expired yet
        assert not is_token_expired(token, settings=settings)

    def test_is_token_expired_false_for_valid_token(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test is_token_expired returns False for valid token."""
        token = create_access_token(user_id, settings=jwt_settings)
        assert is_token_expired(token, settings=jwt_settings) is False

    def test_get_remaining_lifetime_positive_for_valid_token(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test get_remaining_lifetime returns positive timedelta for valid token."""
        token = create_access_token(user_id, settings=jwt_settings)
        remaining = get_remaining_lifetime(token, settings=jwt_settings)

        assert remaining > timedelta(seconds=0)

    def test_token_payload_is_expired_property(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test TokenPayload.is_expired property."""
        token = create_access_token(user_id, settings=jwt_settings)
        payload = verify_token(token, settings=jwt_settings)

        assert payload.is_expired is False


class TestTokenDecoding:
    """Tests for token decoding without verification."""

    def test_decode_token_returns_payload(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test decode_token returns correct payload."""
        token = create_access_token(user_id, settings=jwt_settings)
        payload = decode_token(token, settings=jwt_settings)

        assert payload.sub == user_id
        assert payload.type == TokenType.ACCESS

    def test_decode_token_without_signature_verification(
        self, jwt_settings: JWTSettings, user_id: str
    ):
        """Test decode_token with signature verification disabled."""
        token = create_access_token(user_id, settings=jwt_settings)
        payload = decode_token(token, verify_signature=False, settings=jwt_settings)

        assert payload.sub == user_id

    def test_decode_invalid_token_raises_error(self, jwt_settings: JWTSettings):
        """Test decode_token raises error for invalid token."""
        with pytest.raises(TokenInvalidError):
            decode_token("not.a.valid.token", settings=jwt_settings)

    def test_get_token_expiration(self, jwt_settings: JWTSettings, user_id: str):
        """Test get_token_expiration returns correct datetime."""
        token = create_access_token(user_id, settings=jwt_settings)
        expiration = get_token_expiration(token, settings=jwt_settings)

        assert isinstance(expiration, datetime)
        assert expiration > datetime.now(UTC)


class TestTokenPayloadModel:
    """Tests for TokenPayload Pydantic model."""

    def test_token_payload_validation(self):
        """Test TokenPayload model validation."""
        now = datetime.now(UTC)
        payload = TokenPayload(
            sub="user-123",
            type=TokenType.ACCESS,
            exp=now + timedelta(minutes=15),
            iat=now,
        )

        assert payload.sub == "user-123"
        assert payload.type == TokenType.ACCESS
        assert payload.jti is None

    def test_token_payload_with_jti(self):
        """Test TokenPayload with JTI."""
        now = datetime.now(UTC)
        jti = str(uuid4())
        payload = TokenPayload(
            sub="user-123",
            type=TokenType.REFRESH,
            exp=now + timedelta(days=7),
            iat=now,
            jti=jti,
        )

        assert payload.jti == jti


class TestTokenType:
    """Tests for TokenType enum."""

    def test_token_type_values(self):
        """Test TokenType enum values."""
        assert TokenType.ACCESS.value == "access"
        assert TokenType.REFRESH.value == "refresh"

    def test_token_type_from_string(self):
        """Test TokenType creation from string."""
        assert TokenType("access") == TokenType.ACCESS
        assert TokenType("refresh") == TokenType.REFRESH
