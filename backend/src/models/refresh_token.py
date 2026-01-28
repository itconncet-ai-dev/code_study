"""
RefreshToken SQLAlchemy Model - AI Code Learning Platform

This module defines the RefreshToken entity for JWT authentication.
RefreshTokens are used to issue new access tokens without requiring
the user to re-authenticate.

Reference: data-model.md §RefreshToken entity
Task: T024 - Create RefreshToken SQLAlchemy model
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.user import User


class RefreshToken(Base, UUIDPrimaryKeyMixin):
    """
    RefreshToken entity for JWT authentication.

    Stores hashed refresh tokens with expiration and revocation tracking.
    Tokens are issued during login and used to obtain new access tokens.

    Attributes:
        id: UUID primary key (auto-generated)
        user_id: Foreign key to User (required, cascade delete)
        token_hash: SHA-256 hash of the refresh token (unique, never store plaintext)
        expires_at: Token expiration timestamp (typically 7 days from creation)
        created_at: Token creation timestamp (auto-set)
        revoked: Whether token has been revoked (default False)
        revoked_at: When token was revoked (nullable)

    Relationships:
        user: The User who owns this token

    Business Rules:
        - Tokens expire after 7 days (configured at service level)
        - Rotate on use (issue new, revoke old)
        - Store hash only (never plaintext for security)
        - Revoke on logout
        - Cascade delete when parent User is deleted
    """

    __tablename__ = "refresh_tokens"

    # Foreign key to User (required, cascade delete)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Token hash - SHA-256 hash, unique, never store plaintext
    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Expiration timestamp (required)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Creation timestamp (auto-set)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Revocation tracking
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    def __init__(
        self,
        user_id: uuid.UUID | None = None,
        token_hash: str | None = None,
        expires_at: datetime | None = None,
        revoked: bool = False,
        revoked_at: datetime | None = None,
        **kwargs,
    ):
        """
        Initialize RefreshToken with Python-side defaults.

        SQLAlchemy 2.0 mapped_column defaults are applied at flush time,
        so we explicitly set them here for immediate availability.

        Args:
            user_id: UUID of the token owner (required at persist time)
            token_hash: SHA-256 hash of the refresh token (required at persist time)
            expires_at: Token expiration timestamp (required at persist time)
            revoked: Whether token is revoked (default False)
            revoked_at: When token was revoked (optional)
            **kwargs: Additional SQLAlchemy fields (id, created_at)
        """
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()

        super().__init__(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=revoked,
            revoked_at=revoked_at,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<RefreshToken(id={self.id}, user_id={self.user_id}, "
            f"revoked={self.revoked})>"
        )

    def is_expired(self) -> bool:
        """
        Check if the token has expired.

        Returns:
            True if current time is past expires_at, False otherwise.
        """
        from datetime import timezone

        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """
        Check if the token is valid (not expired and not revoked).

        Returns:
            True if token is usable, False otherwise.
        """
        return not self.revoked and not self.is_expired()
