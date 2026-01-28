"""
UploadedCode SQLAlchemy Model - AI Code Learning Platform

This module defines the UploadedCode entity which stores metadata and content
for code uploaded by users. Each task has exactly one uploaded code record.

Reference: data-model.md §UploadedCode entity
Task: T062 - Create UploadedCode SQLAlchemy model
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.code_file import CodeFile
    from src.models.task import Task


class UploadedCode(Base, UUIDPrimaryKeyMixin):
    """
    UploadedCode entity storing metadata for code uploaded by a user.

    Each task has exactly one UploadedCode record that contains aggregate
    information about the uploaded code (detected language, complexity,
    line counts, file counts, and total size).

    Attributes:
        id: UUID primary key (auto-generated)
        task_id: Foreign key to Task (one-to-one, unique)
        detected_language: Programming language detected (e.g., 'python', 'javascript')
        complexity_level: Assessed complexity ('beginner', 'intermediate', 'advanced')
        total_lines: Total lines of code across all files
        total_files: Number of files uploaded
        upload_size_bytes: Total size in bytes (max 10MB per FR-014)
        created_at: Upload timestamp (auto-set)

    Relationships:
        task: Parent Task (back_populates="uploaded_code")
        code_files: One-to-many relationship to CodeFile (back_populates="uploaded_code")

    Business Rules:
        - Maximum upload size 10MB (FR-014)
        - One uploaded code per task (enforced by unique constraint)
        - Permanently deleted when task is permanently deleted (CASCADE)
        - Complexity levels must be 'beginner', 'intermediate', or 'advanced'
    """

    __tablename__ = "uploaded_code"

    # Foreign key to Task (one-to-one relationship)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Detected programming language (e.g., 'python', 'javascript', 'typescript')
    detected_language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Complexity assessment level
    # Validated at service layer to ensure valid values
    complexity_level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Total lines of code across all files
    total_lines: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Number of files uploaded
    total_files: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Total size in bytes (max 10485760 = 10MB, validated at service layer)
    upload_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="uploaded_code",
        lazy="selectin",
    )

    # One-to-many relationship to CodeFile
    code_files: Mapped[list["CodeFile"]] = relationship(
        "CodeFile",
        back_populates="uploaded_code",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Valid complexity levels (for validation)
    VALID_COMPLEXITY_LEVELS = frozenset({"beginner", "intermediate", "advanced"})

    # Maximum upload size in bytes (10MB)
    MAX_UPLOAD_SIZE_BYTES = 10485760

    def __init__(
        self,
        task_id: uuid.UUID | None = None,
        detected_language: str | None = None,
        complexity_level: str | None = None,
        total_lines: int | None = None,
        total_files: int | None = None,
        upload_size_bytes: int | None = None,
        **kwargs,
    ):
        """
        Initialize UploadedCode with Python-side defaults.

        SQLAlchemy 2.0 mapped_column defaults are applied at flush time,
        so we explicitly set them here for immediate availability.

        Args:
            task_id: Parent task's UUID (required at persist time)
            detected_language: Detected programming language
            complexity_level: Assessed complexity level ('beginner', 'intermediate', 'advanced')
            total_lines: Total lines of code
            total_files: Number of files uploaded
            upload_size_bytes: Total size in bytes (max 10MB)
            **kwargs: Additional SQLAlchemy fields (id, created_at, etc.)
        """
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()

        super().__init__(
            task_id=task_id,
            detected_language=detected_language,
            complexity_level=complexity_level,
            total_lines=total_lines,
            total_files=total_files,
            upload_size_bytes=upload_size_bytes,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<UploadedCode(id={self.id}, task_id={self.task_id}, "
            f"language={self.detected_language}, files={self.total_files}, "
            f"lines={self.total_lines})>"
        )

    def is_valid_complexity_level(self, level: str | None) -> bool:
        """
        Check if a complexity level value is valid.

        Args:
            level: Complexity level to validate

        Returns:
            True if level is valid or None, False otherwise
        """
        if level is None:
            return True
        return level in self.VALID_COMPLEXITY_LEVELS

    def is_within_size_limit(self) -> bool:
        """
        Check if upload size is within the 10MB limit.

        Returns:
            True if size is within limit or None, False otherwise
        """
        if self.upload_size_bytes is None:
            return True
        return self.upload_size_bytes <= self.MAX_UPLOAD_SIZE_BYTES

    @property
    def size_in_mb(self) -> float | None:
        """
        Get upload size in megabytes.

        Returns:
            Size in MB, or None if not set
        """
        if self.upload_size_bytes is None:
            return None
        return round(self.upload_size_bytes / 1048576, 2)

    @property
    def is_multi_file(self) -> bool:
        """
        Check if this is a multi-file upload.

        Returns:
            True if more than one file was uploaded
        """
        return self.total_files is not None and self.total_files > 1
