"""
CodeFile SQLAlchemy Model - AI Code Learning Platform

This module defines the CodeFile entity representing an individual code file
within an uploaded code set. Each UploadedCode can have multiple CodeFiles.

Reference: data-model.md §CodeFile entity
Task: T063 - Create CodeFile SQLAlchemy model
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from src.models.uploaded_code import UploadedCode


class CodeFile(Base, UUIDPrimaryKeyMixin):
    """
    CodeFile entity representing an individual code file within an uploaded code set.

    Each UploadedCode can have multiple CodeFiles (1-20 files per upload).
    CodeFiles store metadata about individual files and the path to the actual
    file content on the filesystem.

    Attributes:
        id: UUID primary key (auto-generated)
        uploaded_code_id: Foreign key to UploadedCode (parent)
        file_name: Original filename as uploaded by user
        file_path: Relative path within folder structure (for folder uploads)
        file_extension: File extension for validation (e.g., '.py', '.js')
        file_size_bytes: Individual file size in bytes
        storage_path: Actual path to file in storage system
        mime_type: MIME type for validation
        created_at: File upload timestamp (auto-set)

    Relationships:
        uploaded_code: Parent UploadedCode (back_populates="code_files")

    Business Rules:
        - Only supported extensions allowed (FR-015)
        - Binary files rejected (FR-016)
        - 1-20 files per upload (FR-018)
        - Permanently deleted when UploadedCode is deleted (CASCADE)
    """

    __tablename__ = "code_files"

    # Foreign key to UploadedCode (parent)
    uploaded_code_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_code.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Original filename as uploaded
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Relative path within folder structure (for folder uploads)
    # e.g., "src/components/Button.tsx" for a folder upload
    file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # File extension for validation
    # Validated at service layer to ensure supported extensions
    file_extension: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Individual file size in bytes
    file_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Actual path to file in storage system
    # e.g., "storage/uploads/{user_id}/{task_id}/{uuid}.py"
    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # MIME type for validation
    mime_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Code content stored in database (for distributed worker access)
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    uploaded_code: Mapped[UploadedCode] = relationship(
        "UploadedCode",
        back_populates="code_files",
        lazy="selectin",
    )

    # Supported file extensions (FR-015)
    SUPPORTED_EXTENSIONS = frozenset(
        {
            ".py",  # Python
            ".js",  # JavaScript
            ".ts",  # TypeScript
            ".jsx",  # React JSX
            ".tsx",  # React TSX
            ".html",  # HTML
            ".css",  # CSS
            ".java",  # Java
            ".cpp",  # C++
            ".c",  # C
            ".txt",  # Text
            ".md",  # Markdown
        }
    )

    # Maximum files per upload (FR-018)
    MAX_FILES_PER_UPLOAD = 20

    # Minimum files per upload
    MIN_FILES_PER_UPLOAD = 1

    def __init__(
        self,
        uploaded_code_id: uuid.UUID | None = None,
        file_name: str | None = None,
        file_path: str | None = None,
        file_extension: str | None = None,
        file_size_bytes: int | None = None,
        storage_path: str | None = None,
        mime_type: str | None = None,
        content: str | None = None,
        **kwargs,
    ):
        """
        Initialize CodeFile with Python-side defaults.

        SQLAlchemy 2.0 mapped_column defaults are applied at flush time,
        so we explicitly set them here for immediate availability.

        Args:
            uploaded_code_id: Parent UploadedCode's UUID (required at persist time)
            file_name: Original filename (required at persist time)
            file_path: Relative path within folder structure
            file_extension: File extension (e.g., '.py')
            file_size_bytes: File size in bytes
            storage_path: Path to actual file in storage (required at persist time)
            mime_type: MIME type
            content: Code content text (for distributed worker access)
            **kwargs: Additional SQLAlchemy fields (id, created_at, etc.)
        """
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()

        super().__init__(
            uploaded_code_id=uploaded_code_id,
            file_name=file_name,
            file_path=file_path,
            file_extension=file_extension,
            file_size_bytes=file_size_bytes,
            storage_path=storage_path,
            mime_type=mime_type,
            content=content,
            **kwargs,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<CodeFile(id={self.id}, file_name={self.file_name}, "
            f"extension={self.file_extension}, size={self.file_size_bytes})>"
        )

    def is_supported_extension(self) -> bool:
        """
        Check if the file extension is in the supported list.

        Returns:
            True if extension is supported or None, False otherwise
        """
        if self.file_extension is None:
            return True
        return self.file_extension.lower() in self.SUPPORTED_EXTENSIONS

    @property
    def size_in_kb(self) -> float | None:
        """
        Get file size in kilobytes.

        Returns:
            Size in KB, or None if not set
        """
        if self.file_size_bytes is None:
            return None
        return round(self.file_size_bytes / 1024, 2)

    @property
    def size_in_mb(self) -> float | None:
        """
        Get file size in megabytes.

        Returns:
            Size in MB, or None if not set
        """
        if self.file_size_bytes is None:
            return None
        return round(self.file_size_bytes / 1048576, 2)

    @property
    def full_path(self) -> str:
        """
        Get the full display path (file_path if available, otherwise file_name).

        Returns:
            The file_path if set, otherwise the file_name
        """
        return self.file_path or self.file_name

    @classmethod
    def extract_extension(cls, filename: str) -> str | None:
        """
        Extract file extension from filename.

        Args:
            filename: The filename to extract extension from

        Returns:
            The extension including the dot (e.g., '.py'), or None if no extension
        """
        if "." not in filename:
            return None
        return "." + filename.rsplit(".", 1)[-1].lower()
