"""
Unit Tests for UserService - T025

TDD RED Phase: These tests define the expected behavior of the UserService.
All tests should FAIL initially until the service is implemented.

Test Coverage:
- register: Create new user with email/password
- register: Hash password before storing
- register: Reject duplicate email
- register: Reject invalid email format
- register: Reject weak password
- login: Authenticate with valid credentials
- login: Return user on successful login
- login: Reject invalid password
- login: Reject non-existent email
- login: Update last_login_at timestamp
- get_by_id: Retrieve user by UUID
- get_by_email: Retrieve user by email
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestUserServiceRegister:
    """Test suite for UserService.register() method."""

    @pytest.mark.asyncio
    async def test_register_creates_new_user(self):
        """register() should create a new user with provided email."""
        from src.services.auth.user_service import UserService

        # Mock the database session
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock no existing user
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.register(
            email="newuser@example.com", password="SecurePass123!"
        )

        assert user is not None
        assert user.email == "newuser@example.com"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_hashes_password(self):
        """register() should hash the password before storing."""
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.register(
            email="test@example.com", password="SecurePass123!"
        )

        # Password should be hashed (bcrypt starts with $2b$)
        assert user.password_hash is not None
        assert user.password_hash.startswith("$2b$")
        assert user.password_hash != "SecurePass123!"

    @pytest.mark.asyncio
    async def test_register_rejects_duplicate_email(self):
        """register() should raise AlreadyExistsError for duplicate email."""
        from src.api.exceptions import AlreadyExistsError
        from src.models.user import User
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()

        # Mock existing user found
        existing_user = User(
            email="existing@example.com", password_hash="$2b$12$somehash"
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        with pytest.raises(AlreadyExistsError) as exc_info:
            await service.register(
                email="existing@example.com", password="SecurePass123!"
            )

        assert "email" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_register_rejects_invalid_email(self):
        """register() should raise ValidationError for invalid email format."""
        from src.api.exceptions import ValidationError
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()
        service = UserService(mock_session)

        with pytest.raises(ValidationError) as exc_info:
            await service.register(email="not-an-email", password="SecurePass123!")

        assert "email" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_register_rejects_weak_password(self):
        """register() should raise ValidationError for weak password."""
        from src.api.exceptions import ValidationError
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()
        service = UserService(mock_session)

        # Password too short (minimum 8 characters per api-spec.yaml)
        with pytest.raises(ValidationError) as exc_info:
            await service.register(email="test@example.com", password="short")

        assert "password" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_register_sets_default_skill_level(self):
        """register() should set skill_level to 'Complete Beginner'."""
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.register(
            email="test@example.com", password="SecurePass123!"
        )

        assert user.skill_level == "Complete Beginner"


class TestUserServiceLogin:
    """Test suite for UserService.login() method."""

    @pytest.mark.asyncio
    async def test_login_returns_user_on_valid_credentials(self):
        """login() should return user for valid email and password."""
        from src.models.user import User
        from src.services.auth.user_service import UserService
        from src.utils.security import hash_password

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()

        # Create mock user with hashed password
        hashed_password = hash_password("CorrectPass123!")
        existing_user = User(email="user@example.com", password_hash=hashed_password)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.login(email="user@example.com", password="CorrectPass123!")

        assert user is not None
        assert user.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_login_updates_last_login_at(self):
        """login() should update the user's last_login_at timestamp."""
        from src.models.user import User
        from src.services.auth.user_service import UserService
        from src.utils.security import hash_password

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()

        hashed_password = hash_password("CorrectPass123!")
        existing_user = User(email="user@example.com", password_hash=hashed_password)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.login(email="user@example.com", password="CorrectPass123!")

        assert user.last_login_at is not None
        assert isinstance(user.last_login_at, datetime)
        mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_login_rejects_invalid_password(self):
        """login() should raise InvalidCredentialsError for wrong password."""
        from src.api.exceptions import InvalidCredentialsError
        from src.models.user import User
        from src.services.auth.user_service import UserService
        from src.utils.security import hash_password

        mock_session = AsyncMock()

        hashed_password = hash_password("CorrectPass123!")
        existing_user = User(email="user@example.com", password_hash=hashed_password)

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        with pytest.raises(InvalidCredentialsError):
            await service.login(email="user@example.com", password="WrongPassword123!")

    @pytest.mark.asyncio
    async def test_login_rejects_nonexistent_email(self):
        """login() should raise InvalidCredentialsError for unknown email."""
        from src.api.exceptions import InvalidCredentialsError
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()

        # Mock no user found
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)

        with pytest.raises(InvalidCredentialsError):
            await service.login(
                email="nonexistent@example.com", password="SomePassword123!"
            )


class TestUserServiceGetters:
    """Test suite for UserService getter methods."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_user(self):
        """get_by_id() should return user for valid UUID."""
        from src.models.user import User
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        existing_user = User(
            id=user_id, email="user@example.com", password_hash="$2b$12$somehash"
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.get_by_id(user_id)

        assert user is not None
        assert user.id == user_id

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_unknown_id(self):
        """get_by_id() should return None for unknown UUID."""
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.get_by_id(uuid.uuid4())

        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email_returns_user(self):
        """get_by_email() should return user for valid email."""
        from src.models.user import User
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()

        existing_user = User(email="user@example.com", password_hash="$2b$12$somehash")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.get_by_email("user@example.com")

        assert user is not None
        assert user.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_returns_none_for_unknown_email(self):
        """get_by_email() should return None for unknown email."""
        from src.services.auth.user_service import UserService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = UserService(mock_session)
        user = await service.get_by_email("unknown@example.com")

        assert user is None
