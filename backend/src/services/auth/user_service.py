"""
User Service - AI Code Learning Platform

This module provides the UserService for user authentication operations
including registration, login, and user retrieval.

Features:
- User registration with email validation and password hashing
- User login with credential verification
- User retrieval by ID or email
- Last login timestamp tracking

Usage:
    from src.services.auth.user_service import UserService

    # In FastAPI endpoint with dependency injection
    async def register_user(
        request: RegisterRequest,
        db: AsyncSession = Depends(get_db)
    ):
        service = UserService(db)
        user = await service.register(request.email, request.password)
        return user

Reference: data-model.md §User entity
Task: T025 - Implement UserService (register, login, logout)
"""

import re
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import (
    AlreadyExistsError,
    InvalidCredentialsError,
    ValidationError,
)
from src.models.user import User
from src.utils.security import hash_password, verify_password

# Email validation regex per RFC 5322 simplified
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Minimum password length per api-spec.yaml
MIN_PASSWORD_LENGTH = 8


class UserService:
    """
    Service class for user authentication operations.

    Provides methods for user registration, login, and retrieval.
    All operations are async and use SQLAlchemy AsyncSession.

    Attributes:
        db: AsyncSession for database operations

    Example:
        service = UserService(db_session)
        user = await service.register("user@example.com", "SecurePass123!")
        logged_in_user = await service.login("user@example.com", "SecurePass123!")
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize UserService with database session.

        Args:
            db: SQLAlchemy AsyncSession for database operations
        """
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
    ) -> User:
        """
        Register a new user with email and password.

        Creates a new user account after validating email format,
        password strength, and ensuring email uniqueness.

        Args:
            email: User's email address (must be unique and valid format)
            password: Plain-text password (minimum 8 characters)

        Returns:
            User: The newly created user instance

        Raises:
            ValidationError: If email format is invalid or password too weak
            AlreadyExistsError: If email is already registered

        Example:
            user = await service.register("new@example.com", "SecurePass123!")
        """
        # Validate email format
        self._validate_email(email)

        # Validate password strength
        self._validate_password(password)

        # Check for existing user with same email
        existing_user = await self.get_by_email(email)
        if existing_user is not None:
            raise AlreadyExistsError(
                detail="A user with this email already exists",
                resource="user",
                field="email",
                value=email,
            )

        # Hash the password
        password_hash = hash_password(password)

        # Create new user
        user = User(
            email=email,
            password_hash=password_hash,
            skill_level="Complete Beginner",
        )

        # Persist to database
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login(
        self,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate a user with email and password.

        Verifies credentials and updates the last_login_at timestamp
        on successful authentication.

        Args:
            email: User's email address
            password: Plain-text password to verify

        Returns:
            User: The authenticated user instance

        Raises:
            InvalidCredentialsError: If email not found or password incorrect

        Example:
            user = await service.login("user@example.com", "CorrectPass123!")

        Security Notes:
            - Uses timing-safe password comparison to prevent timing attacks
            - Same error message for invalid email and password to prevent enumeration
        """
        # Find user by email
        user = await self.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError(detail="Invalid email or password")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError(detail="Invalid email or password")

        # Update last login timestamp
        user.last_login_at = datetime.now(UTC)
        await self.db.commit()

        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieve a user by their UUID.

        Args:
            user_id: The user's unique identifier

        Returns:
            User: The user instance if found, None otherwise

        Example:
            user = await service.get_by_id(uuid.UUID("..."))
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email: The user's email address

        Returns:
            User: The user instance if found, None otherwise

        Example:
            user = await service.get_by_email("user@example.com")
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _validate_email(self, email: str) -> None:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Raises:
            ValidationError: If email format is invalid
        """
        if not email or not EMAIL_REGEX.match(email):
            raise ValidationError(
                detail="Invalid email format",
                field="email",
            )

    def _validate_password(self, password: str) -> None:
        """
        Validate password strength.

        Checks minimum length requirement per api-spec.yaml.

        Args:
            password: Password to validate

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(
                detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
                field="password",
            )
