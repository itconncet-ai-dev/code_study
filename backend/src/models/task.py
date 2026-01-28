"""
Task SQLAlchemy Model - AI Code Learning Platform

This module defines the Task entity representing a single learning unit
focused on one code upload. Tasks support soft delete with 30-day trash retention.

Reference: data-model.md §Task entity
Task: T061 - Create Task SQLAlchemy model with sequential task_number
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.learning_document import LearningDocument
    from src.models.project import Project
    from src.models.uploaded_code import UploadedCode


class Task(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Task entity representing a single learning unit focused on one code upload.

    Tasks belong to a Project and contain uploaded code that will be analyzed
    and converted into learning documents. Supports soft delete with 30-day
    trash retention.

    Attributes:
        id: UUID primary key (auto-generated)
        project_id: Foreign key to Project (parent container)
        task_number: Sequential number within project (immutable once assigned)
        title: Task name (required, minimum 5 characters per FR-008)
        description: Optional description (max 500 characters per FR-009)
        upload_method: How code was uploaded ('file', 'folder', 'paste')
        created_at: Task creation timestamp (auto-set)
        updated_at: Last modification timestamp (auto-updated)
        deletion_status: 'active' or 'trashed' (via SoftDeleteMixin)
        trashed_at: When task was moved to trash (via SoftDeleteMixin)
        scheduled_deletion_at: When task will be permanently deleted (via SoftDeleteMixin)

    Relationships:
        project: Parent Project (back_populates="tasks")
        uploaded_code: One-to-one relationship to UploadedCode (back_populates="task")
        learning_document: One-to-one relationship to LearningDocument (back_populates="task")
        practice_problems: One-to-many relationship to PracticeProblem (to be added)
        questions: One-to-many relationship to Question (to be added)
        progress: One-to-one relationship to Progress (to be added)

    Business Rules:
        - Task numbers are sequential and immutable (FR-004)
        - Users cannot reorder tasks (FR-005)
        - Title min 5 chars, description max 500 chars
        - Soft delete preserves task for 30 days
        - Task number is unique within each project
    """

    __tablename__ = "tasks"

    # Unique constraint for task_number within project
    __table_args__ = (
        UniqueConstraint(
            "project_id", "task_number", name="unique_task_number_per_project"
        ),
    )

    # Foreign key to Project (parent)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Sequential task number within project - immutable once assigned
    task_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Title field - required, minimum 5 characters (validated at service layer)
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Description field - optional, max 500 characters (validated at service layer)
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Upload method - how code was uploaded
    upload_method: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Relationships
    project: Mapped[Project] = relationship(
        "Project",
        back_populates="tasks",
        lazy="selectin",
    )

    # One-to-one relationship to UploadedCode
    uploaded_code: Mapped[UploadedCode | None] = relationship(
        "UploadedCode",
        back_populates="task",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # One-to-one relationship to LearningDocument
    learning_document: Mapped[LearningDocument | None] = relationship(
        "LearningDocument",
        back_populates="task",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # NOTE: Additional relationships will be added as models are created:
    # practice_problems: Mapped[list["PracticeProblem"]] = relationship(...)
    # questions: Mapped[list["Question"]] = relationship(...)
    # progress: Mapped["Progress"] = relationship(...)

    def __init__(
        self,
        project_id: uuid.UUID | None = None,
        task_number: int | None = None,
        title: str | None = None,
        description: str | None = None,
        upload_method: str | None = None,
        deletion_status: str = "active",
        trashed_at: datetime | None = None,
        scheduled_deletion_at: datetime | None = None,
        **kwargs,
    ):
        """
        Initialize Task with Python-side defaults.

        SQLAlchemy 2.0 mapped_column defaults are applied at flush time,
        so we explicitly set them here for immediate availability.

        Args:
            project_id: Parent project's UUID (required at persist time)
            task_number: Sequential number within project (required at persist time)
            title: Task name (required at persist time, min 5 chars)
            description: Optional task description (max 500 chars)
            upload_method: How code was uploaded ('file', 'folder', 'paste')
            deletion_status: Defaults to 'active'
            trashed_at: When task was trashed (optional)
            scheduled_deletion_at: When task will be permanently deleted (optional)
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
            project_id=project_id,
            task_number=task_number,
            title=title,
            description=description,
            upload_method=upload_method,
            deletion_status=deletion_status,
            trashed_at=trashed_at,
            scheduled_deletion_at=scheduled_deletion_at,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Task(id={self.id}, project_id={self.project_id}, task_number={self.task_number}, title={self.title})>"

    def soft_delete(self, scheduled_deletion: datetime) -> None:
        """
        Move task to trash with scheduled permanent deletion.

        Args:
            scheduled_deletion: When the task should be permanently deleted
                               (typically trashed_at + 30 days)
        """
        self.deletion_status = "trashed"
        self.trashed_at = datetime.now()
        self.scheduled_deletion_at = scheduled_deletion

    def restore(self) -> None:
        """
        Restore task from trash to active status.

        Clears trashed_at and scheduled_deletion_at, sets status to 'active'.
        """
        self.deletion_status = "active"
        self.trashed_at = None
        self.scheduled_deletion_at = None

    @property
    def is_trashed(self) -> bool:
        """Check if task is in trash."""
        return self.deletion_status == "trashed"

    @property
    def is_active(self) -> bool:
        """Check if task is active (not trashed)."""
        return self.deletion_status == "active"
