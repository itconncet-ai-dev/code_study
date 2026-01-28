"""
User SQLAlchemy Model - AI Code Learning Platform

This module defines the User entity for authentication and user management.
Users own Projects and RefreshTokens, with profile information including
skill level tracking.

Reference: data-model.md §User entity
Task: T023 - Create User SQLAlchemy model
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.refresh_token import RefreshToken
    from src.models.project import Project


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User entity representing a platform user.

    Stores authentication credentials and profile information.
    All users default to 'Complete Beginner' skill level per constitution.

    Attributes:
        id: UUID primary key (auto-generated)
        email: Unique email address for login (validated format)
        password_hash: bcrypt hashed password (cost factor 12)
        skill_level: User's self-reported skill level, defaults to 'Complete Beginner'
        created_at: Account creation timestamp (auto-set)
        updated_at: Last profile update timestamp (auto-updated)
        last_login_at: Last successful login timestamp (nullable)

    Relationships:
        projects: User's owned projects (cascade delete)
        refresh_tokens: Active refresh tokens for JWT auth (cascade delete)

    Business Rules:
        - Email must be unique across all users
        - Password must be hashed before storage (never store plaintext)
        - skill_level defaults to 'Complete Beginner' per constitution
    """

    __tablename__ = "users"

    # Email field - unique, required, validated at application level
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Password hash - bcrypt hashed, never store plaintext
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Skill level - default 'Complete Beginner' per constitution
    skill_level: Mapped[str] = mapped_column(
        String(50),
        default="Complete Beginner",
        nullable=False,
    )

    # Last login timestamp - nullable, updated on successful login
    last_login_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Relationships
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(
        self,
        email: str | None = None,
        password_hash: str | None = None,
        skill_level: str = "Complete Beginner",
        last_login_at: datetime | None = None,
        **kwargs,
    ):
        """
        Initialize User with Python-side defaults.

        SQLAlchemy 2.0 mapped_column defaults are applied at flush time,
        so we explicitly set them here for immediate availability.

        Args:
            email: User's email address (required at persist time)
            password_hash: bcrypt hashed password (required at persist time)
            skill_level: Defaults to 'Complete Beginner'
            last_login_at: Last login timestamp (optional)
            **kwargs: Additional SQLAlchemy fields (id, created_at, updated_at)
        """
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()

        super().__init__(
            email=email,
            password_hash=password_hash,
            skill_level=skill_level,
            last_login_at=last_login_at,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email={self.email})>"
