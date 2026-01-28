"""
LearningDocument SQLAlchemy Model - AI Code Learning Platform

This module defines the LearningDocument entity representing the AI-generated
7-chapter educational content for a task's code. The document is stored as
JSONB and generated asynchronously via Celery.

Reference: data-model.md §LearningDocument entity
Task: T090 - Create LearningDocument SQLAlchemy model with JSONB content
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.task import Task


class LearningDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    LearningDocument entity representing AI-generated educational content.

    Each task has one learning document containing 7 chapters that explain
    the uploaded code in a beginner-friendly format. Documents are generated
    asynchronously and stored as JSONB for flexible content structure.

    Attributes:
        id: UUID primary key (auto-generated)
        task_id: Foreign key to Task (one-to-one relationship)
        content: JSONB containing 7 chapters (see structure below)
        generation_status: 'pending', 'in_progress', 'completed', 'failed'
        generation_started_at: When generation began
        generation_completed_at: When generation finished
        generation_error: Error message if generation failed
        celery_task_id: Celery task ID for async status tracking
        created_at: Document creation timestamp (auto-set)
        updated_at: Last modification timestamp (auto-updated)

    JSONB Content Structure:
        {
            "chapter1": {
                "title": "What This Code Does",
                "summary": "One-sentence plain language summary"
            },
            "chapter2": {
                "title": "Prerequisites Knowledge",
                "concepts": [
                    {
                        "name": "Variables",
                        "explanation": "...",
                        "analogy": "...",
                        "example": "...",
                        "use_cases": "..."
                    }
                ]
            },
            "chapter3": {
                "title": "Code Structure Overview",
                "flowchart": "ASCII/Mermaid diagram",
                "file_breakdown": {...}
            },
            "chapter4": {
                "title": "Line-by-Line Explanation",
                "explanations": [...]
            },
            "chapter5": {
                "title": "Execution Flow Simulation",
                "steps": [...]
            },
            "chapter6": {
                "title": "Core Concepts Summary",
                "concepts": [...]
            },
            "chapter7": {
                "title": "Common Mistakes",
                "mistakes": [
                    {"wrong": "...", "right": "...", "why": "...", "fix": "..."}
                ]
            }
        }

    Relationships:
        task: Parent Task (back_populates="learning_document")

    Business Rules:
        - One document per task (one-to-one relationship)
        - Immutable after generation (FR-038 - content immutability)
        - Generate within 3 minutes for 500 LOC (FR-083)
        - Stored, not regenerated on view (FR-038)
        - Deleted when parent task is permanently deleted (CASCADE)
    """

    __tablename__ = "learning_documents"

    # Foreign key to Task (one-to-one, unique)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # JSONB content containing 7 chapters
    # Note: Validation of chapter structure is done at service layer per constitution
    content: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Generation status tracking
    generation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    # Timestamps for generation tracking
    generation_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    generation_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Error message if generation failed
    generation_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Celery task ID for async status tracking
    celery_task_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # Relationship to parent Task
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="learning_document",
        lazy="selectin",
    )

    # Valid generation statuses
    VALID_STATUSES = ("pending", "in_progress", "completed", "failed")

    # Required chapters in content
    REQUIRED_CHAPTERS = (
        "chapter1",
        "chapter2",
        "chapter3",
        "chapter4",
        "chapter5",
        "chapter6",
        "chapter7",
    )

    def __init__(
        self,
        task_id: uuid.UUID | None = None,
        content: dict[str, Any] | None = None,
        generation_status: str = "pending",
        generation_started_at: datetime | None = None,
        generation_completed_at: datetime | None = None,
        generation_error: str | None = None,
        celery_task_id: str | None = None,
        **kwargs,
    ):
        """
        Initialize LearningDocument with Python-side defaults.

        Args:
            task_id: Parent task's UUID (required at persist time)
            content: JSONB content with 7 chapters (defaults to empty dict)
            generation_status: Status of document generation (defaults to 'pending')
            generation_started_at: When generation began (optional)
            generation_completed_at: When generation finished (optional)
            generation_error: Error message if failed (optional)
            celery_task_id: Celery task ID for tracking (optional)
            **kwargs: Additional SQLAlchemy fields (id, created_at, updated_at, etc.)
        """
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()

        if content is None:
            content = {}

        super().__init__(
            task_id=task_id,
            content=content,
            generation_status=generation_status,
            generation_started_at=generation_started_at,
            generation_completed_at=generation_completed_at,
            generation_error=generation_error,
            celery_task_id=celery_task_id,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<LearningDocument(id={self.id}, task_id={self.task_id}, "
            f"status={self.generation_status})>"
        )

    def start_generation(self, celery_task_id: str) -> None:
        """
        Mark document generation as started.

        Args:
            celery_task_id: The Celery task ID for tracking
        """
        self.generation_status = "in_progress"
        self.generation_started_at = datetime.now()
        self.celery_task_id = celery_task_id
        self.generation_error = None

    def complete_generation(self, content: dict[str, Any]) -> None:
        """
        Mark document generation as completed with the generated content.

        Args:
            content: The generated 7-chapter document content

        Raises:
            ValueError: If content does not contain all required chapters
        """
        missing_chapters = set(self.REQUIRED_CHAPTERS) - set(content.keys())
        if missing_chapters:
            raise ValueError(
                f"Content missing required chapters: {', '.join(sorted(missing_chapters))}"
            )

        self.generation_status = "completed"
        self.generation_completed_at = datetime.now()
        self.content = content
        self.generation_error = None

    def fail_generation(self, error_message: str) -> None:
        """
        Mark document generation as failed with an error message.

        Args:
            error_message: Description of the failure
        """
        self.generation_status = "failed"
        self.generation_completed_at = datetime.now()
        self.generation_error = error_message

    @property
    def is_pending(self) -> bool:
        """Check if document generation is pending."""
        return self.generation_status == "pending"

    @property
    def is_in_progress(self) -> bool:
        """Check if document generation is in progress."""
        return self.generation_status == "in_progress"

    @property
    def is_completed(self) -> bool:
        """Check if document generation is completed."""
        return self.generation_status == "completed"

    @property
    def is_failed(self) -> bool:
        """Check if document generation failed."""
        return self.generation_status == "failed"

    @property
    def has_content(self) -> bool:
        """Check if document has generated content."""
        return bool(self.content) and all(
            chapter in self.content for chapter in self.REQUIRED_CHAPTERS
        )

    @property
    def generation_duration_seconds(self) -> float | None:
        """
        Calculate generation duration in seconds.

        Returns:
            Duration in seconds if both timestamps are available, None otherwise.
        """
        if self.generation_started_at and self.generation_completed_at:
            delta = self.generation_completed_at - self.generation_started_at
            return delta.total_seconds()
        return None

    def get_chapter(self, chapter_number: int) -> dict[str, Any] | None:
        """
        Get a specific chapter from the document content.

        Args:
            chapter_number: Chapter number (1-7)

        Returns:
            Chapter content dict or None if not found
        """
        if not 1 <= chapter_number <= 7:
            return None
        chapter_key = f"chapter{chapter_number}"
        return self.content.get(chapter_key)
