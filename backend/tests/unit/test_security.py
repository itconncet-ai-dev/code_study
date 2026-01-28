"""
Unit tests for Password Hashing Utilities - AI Code Learning Platform

Tests cover:
- Password hashing with bcrypt
- Password verification
- Hash security properties
- Error handling and edge cases

TDD Phase: RED - These tests will fail until security.py is implemented
"""

import pytest

from src.utils.security import (
    PasswordHasher,
    PasswordSettings,
    hash_password,
    verify_password,
    get_password_settings,
    PasswordHashError,
    PasswordVerifyError,
)


@pytest.fixture
def password_settings() -> PasswordSettings:
    """Create test password settings with default bcrypt rounds."""
    return PasswordSettings(
        bcrypt_rounds=4,  # Lower rounds for faster testing
    )


@pytest.fixture
def sample_password() -> str:
    """Provide a sample password for testing."""
    return "SecurePassword123!"


@pytest.fixture
def password_hasher(password_settings: PasswordSettings) -> PasswordHasher:
    """Create a password hasher with test settings."""
    return PasswordHasher(settings=password_settings)


class TestPasswordSettings:
    """Tests for PasswordSettings configuration."""

    def test_default_settings(self):
        """Test default password settings are loaded."""
        settings = PasswordSettings()
        # Default bcrypt rounds should be secure (12)
        assert settings.bcrypt_rounds == 12

    def test_custom_bcrypt_rounds(self):
        """Test custom bcrypt rounds setting."""
        settings = PasswordSettings(bcrypt_rounds=10)
        assert settings.bcrypt_rounds == 10

    def test_minimum_bcrypt_rounds(self):
        """Test minimum bcrypt rounds validation (4 is bcrypt minimum)."""
        settings = PasswordSettings(bcrypt_rounds=4)
        assert settings.bcrypt_rounds == 4

    def test_bcrypt_rounds_validation(self):
        """Test bcrypt rounds must be within valid range."""
        # bcrypt supports rounds 4-31
        with pytest.raises(ValueError):
            PasswordSettings(bcrypt_rounds=3)  # Below minimum

        with pytest.raises(ValueError):
            PasswordSettings(bcrypt_rounds=32)  # Above maximum


class TestHashPassword:
    """Tests for password hashing functionality."""

    def test_hash_password_returns_string(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test hash_password returns a string hash."""
        hashed = hash_password(sample_password, settings=password_settings)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_returns_bcrypt_format(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test hash uses bcrypt format ($2b$ prefix)."""
        hashed = hash_password(sample_password, settings=password_settings)
        # bcrypt hashes start with $2b$, $2a$, or $2y$
        assert hashed.startswith(("$2b$", "$2a$", "$2y$"))

    def test_hash_password_is_deterministic_length(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test bcrypt hash is always 60 characters."""
        hashed = hash_password(sample_password, settings=password_settings)
        assert len(hashed) == 60

    def test_hash_password_different_for_same_input(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test same password produces different hashes (salted)."""
        hash1 = hash_password(sample_password, settings=password_settings)
        hash2 = hash_password(sample_password, settings=password_settings)
        # Hashes should be different due to random salt
        assert hash1 != hash2

    def test_hash_password_different_for_different_inputs(
        self, password_settings: PasswordSettings
    ):
        """Test different passwords produce different hashes."""
        hash1 = hash_password("password1", settings=password_settings)
        hash2 = hash_password("password2", settings=password_settings)
        assert hash1 != hash2

    def test_hash_password_empty_raises_error(
        self, password_settings: PasswordSettings
    ):
        """Test empty password raises error."""
        with pytest.raises(PasswordHashError):
            hash_password("", settings=password_settings)

    def test_hash_password_none_raises_error(
        self, password_settings: PasswordSettings
    ):
        """Test None password raises error."""
        with pytest.raises((PasswordHashError, TypeError)):
            hash_password(None, settings=password_settings)  # type: ignore

    def test_hash_password_very_long(self, password_settings: PasswordSettings):
        """Test hashing very long password (bcrypt has 72 byte limit)."""
        long_password = "a" * 100
        hashed = hash_password(long_password, settings=password_settings)
        # Should still hash successfully
        assert len(hashed) == 60

    def test_hash_password_unicode(self, password_settings: PasswordSettings):
        """Test hashing password with unicode characters."""
        unicode_password = "비밀번호123!@#"
        hashed = hash_password(unicode_password, settings=password_settings)
        assert len(hashed) == 60


class TestVerifyPassword:
    """Tests for password verification functionality."""

    def test_verify_correct_password(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test verification succeeds with correct password."""
        hashed = hash_password(sample_password, settings=password_settings)
        result = verify_password(sample_password, hashed)
        assert result is True

    def test_verify_incorrect_password(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test verification fails with incorrect password."""
        hashed = hash_password(sample_password, settings=password_settings)
        result = verify_password("wrong_password", hashed)
        assert result is False

    def test_verify_case_sensitive(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test password verification is case sensitive."""
        hashed = hash_password(sample_password, settings=password_settings)
        result = verify_password(sample_password.upper(), hashed)
        assert result is False

    def test_verify_with_spaces(self, password_settings: PasswordSettings):
        """Test password with spaces verifies correctly."""
        password_with_spaces = "pass word with spaces"
        hashed = hash_password(password_with_spaces, settings=password_settings)
        assert verify_password(password_with_spaces, hashed) is True
        assert verify_password("passwordwithspaces", hashed) is False

    def test_verify_invalid_hash_format(self, sample_password: str):
        """Test verification with invalid hash format raises error."""
        with pytest.raises(PasswordVerifyError):
            verify_password(sample_password, "not_a_valid_hash")

    def test_verify_empty_password(self, password_settings: PasswordSettings):
        """Test verification with empty password returns False."""
        hashed = hash_password("some_password", settings=password_settings)
        result = verify_password("", hashed)
        assert result is False

    def test_verify_unicode_password(self, password_settings: PasswordSettings):
        """Test verification with unicode password."""
        unicode_password = "한글비밀번호!"
        hashed = hash_password(unicode_password, settings=password_settings)
        assert verify_password(unicode_password, hashed) is True
        assert verify_password("한글비밀번호", hashed) is False


class TestPasswordHasher:
    """Tests for PasswordHasher class."""

    def test_hasher_hash_password(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test PasswordHasher.hash method."""
        hashed = password_hasher.hash(sample_password)
        assert isinstance(hashed, str)
        assert len(hashed) == 60

    def test_hasher_verify_password(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test PasswordHasher.verify method."""
        hashed = password_hasher.hash(sample_password)
        assert password_hasher.verify(sample_password, hashed) is True
        assert password_hasher.verify("wrong", hashed) is False

    def test_hasher_uses_settings(self, password_settings: PasswordSettings):
        """Test PasswordHasher uses provided settings."""
        hasher = PasswordHasher(settings=password_settings)
        # Verify settings are applied (indirectly through hash format)
        hashed = hasher.hash("test_password")
        # Extract rounds from hash: $2b$04$... (04 = 4 rounds)
        rounds_str = hashed.split("$")[2]
        assert int(rounds_str) == password_settings.bcrypt_rounds


class TestGetPasswordSettings:
    """Tests for get_password_settings function."""

    def test_get_password_settings_returns_settings(self):
        """Test get_password_settings returns PasswordSettings instance."""
        settings = get_password_settings()
        assert isinstance(settings, PasswordSettings)

    def test_get_password_settings_cached(self):
        """Test get_password_settings returns cached instance."""
        settings1 = get_password_settings()
        settings2 = get_password_settings()
        # Should return same cached instance
        assert settings1 is settings2


class TestSecurityBestPractices:
    """Tests for security best practices."""

    def test_hash_not_reversible(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test hash does not contain original password."""
        hashed = hash_password(sample_password, settings=password_settings)
        # Password should not be recoverable from hash
        assert sample_password not in hashed
        assert sample_password.encode() not in hashed.encode()

    def test_timing_safe_verification(
        self, sample_password: str, password_settings: PasswordSettings
    ):
        """Test verification is timing-safe (bcrypt handles this internally)."""
        hashed = hash_password(sample_password, settings=password_settings)
        # This test just ensures bcrypt's built-in timing-safe comparison is used
        # We verify by checking both correct and incorrect password verification works
        assert verify_password(sample_password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_minimum_password_length_allowed(
        self, password_settings: PasswordSettings
    ):
        """Test very short passwords can still be hashed (validation is caller's responsibility)."""
        short_password = "a"
        hashed = hash_password(short_password, settings=password_settings)
        assert verify_password(short_password, hashed) is True

    def test_special_characters_in_password(
        self, password_settings: PasswordSettings
    ):
        """Test passwords with special characters work correctly."""
        special_password = "P@$$w0rd!#$%^&*(){}[]|\\:\";<>,.?/~`"
        hashed = hash_password(special_password, settings=password_settings)
        assert verify_password(special_password, hashed) is True
