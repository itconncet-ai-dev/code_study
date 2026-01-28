"""
Project SQLAlchemy Model - AI Code Learning Platform

This module defines the Project entity representing a learning container
for related tasks. Projects support soft delete with 30-day trash retention.

Reference: data-model.md §Project entity
Task: T043 - Create Project SQLAlchemy model with soft delete fields
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.task import Task


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Project entity representing a learning container for related tasks.

    Users create projects to organize their learning tasks. Each project
    can contain multiple tasks with uploaded code and generated documents.
    Supports soft delete with 30-day trash retention.

    Attributes:
        id: UUID primary key (auto-generated)
        user_id: Foreign key to User (owner)
        title: Project name (required, min 1 character)
        description: Optional project description
        created_at: Project creation timestamp (auto-set)
        updated_at: Last modification timestamp (auto-updated)
        last_activity_at: Last task activity timestamp (updated when tasks modified)
        deletion_status: 'active' or 'trashed' (via SoftDeleteMixin)
        trashed_at: When project was moved to trash (via SoftDeleteMixin)
        scheduled_deletion_at: When project will be permanently deleted (via SoftDeleteMixin)

    Relationships:
        user: Owner User (back_populates="projects")
        tasks: Project's tasks (to be added when Task model is created)

    Business Rules:
        - Title required (minimum 1 character)
        - Soft delete: When deleted, all tasks also move to trash
        - After 30 days in trash, permanent deletion cascade to tasks
        - Project can only be accessed by its owner (user_id)
    """

    __tablename__ = "projects"

    # Foreign key to User (owner)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Title field - required, minimum 1 character
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Description field - optional
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Last activity timestamp - tracks when tasks were last modified
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
        lazy="selectin",
    )

    # Tasks relationship - added in T061 when Task model was created
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(
        self,
        user_id: uuid.UUID | None = None,
        title: str | None = None,
        description: str | None = None,
        deletion_status: str = "active",
        trashed_at: datetime | None = None,
        scheduled_deletion_at: datetime | None = None,
        **kwargs,
    ):
        """
        Initialize Project with Python-side defaults.

        SQLAlchemy 2.0 mapped_column defaults are applied at flush time,
        so we explicitly set them here for immediate availability.

        Args:
            user_id: Owner user's UUID (required at persist time)
            title: Project name (required at persist time)
            description: Optional project description
            deletion_status: Defaults to 'active'
            trashed_at: When project was trashed (optional)
            scheduled_deletion_at: When project will be permanently deleted (optional)
            **kwargs: Additional SQLAlchemy fields (id, created_at, updated_at, etc.)
        """
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()

        # Set soft delete defaults
        if deletion_status == "active":
            trashed_at = None
            scheduled_deletion_at = None

        super().__init__(
            user_id=user_id,
            title=title,
            description=description,
            deletion_status=deletion_status,
            trashed_at=trashed_at,
            scheduled_deletion_at=scheduled_deletion_at,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"

    def soft_delete(self, scheduled_deletion: datetime) -> None:
        """
        Move project to trash with scheduled permanent deletion.

        Args:
            scheduled_deletion: When the project should be permanently deleted
                               (typically trashed_at + 30 days)
        """
        self.deletion_status = "trashed"
        self.trashed_at = datetime.now()
        self.scheduled_deletion_at = scheduled_deletion

    def restore(self) -> None:
        """
        Restore project from trash to active status.

        Clears trashed_at and scheduled_deletion_at, sets status to 'active'.
        """
        self.deletion_status = "active"
        self.trashed_at = None
        self.scheduled_deletion_at = None

    @property
    def is_trashed(self) -> bool:
        """Check if project is in trash."""
        return self.deletion_status == "trashed"

    @property
    def is_active(self) -> bool:
        """Check if project is active (not trashed)."""
        return self.deletion_status == "active"
