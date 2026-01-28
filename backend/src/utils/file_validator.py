"""
File Validation Utilities - AI Code Learning Platform

This module provides file validation utilities for code uploads including:
- Extension validation (FR-015)
- File size validation (FR-014)
- Binary file detection (FR-016)
- File count validation (FR-018)

Reference: spec.md §FR-014 through FR-018
Task: T064 - Implement file validation utilities
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


@dataclass
class ValidationResult:
    """Result of a file validation check."""

    is_valid: bool
    error_message: str | None = None

    @classmethod
    def success(cls) -> "ValidationResult":
        """Create a successful validation result."""
        return cls(is_valid=True, error_message=None)

    @classmethod
    def failure(cls, message: str) -> "ValidationResult":
        """Create a failed validation result with error message."""
        return cls(is_valid=False, error_message=message)


class FileValidator:
    """
    File validation utilities for code uploads.

    Validates files against platform requirements:
    - Supported file extensions (FR-015)
    - Maximum file size 10MB (FR-014)
    - No binary files (FR-016)
    - 1-20 files per upload (FR-018)
    """

    # Supported file extensions (FR-015)
    SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({
        ".py",    # Python
        ".js",    # JavaScript
        ".ts",    # TypeScript
        ".jsx",   # React JSX
        ".tsx",   # React TSX
        ".html",  # HTML
        ".css",   # CSS
        ".java",  # Java
        ".cpp",   # C++
        ".c",     # C
        ".txt",   # Text
        ".md",    # Markdown
    })

    # Maximum file size in bytes (10MB per FR-014)
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB = 10,485,760 bytes

    # Maximum total upload size in bytes (10MB per FR-014)
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB

    # File count limits (FR-018)
    MIN_FILES_PER_UPLOAD: int = 1
    MAX_FILES_PER_UPLOAD: int = 20

    # Binary detection threshold
    # If more than this percentage of null bytes, consider it binary
    BINARY_NULL_THRESHOLD: float = 0.1  # 10%

    # Sample size for binary detection (first N bytes)
    BINARY_SAMPLE_SIZE: int = 8192  # 8KB

    @classmethod
    def validate_extension(cls, filename: str) -> ValidationResult:
        """
        Validate that the file has a supported extension.

        Args:
            filename: The filename to validate

        Returns:
            ValidationResult indicating success or failure with message
        """
        extension = cls.extract_extension(filename)

        if extension is None:
            return ValidationResult.failure(
                f"File '{filename}' has no extension. "
                f"Supported extensions: {sorted(cls.SUPPORTED_EXTENSIONS)}"
            )

        if extension.lower() not in cls.SUPPORTED_EXTENSIONS:
            return ValidationResult.failure(
                f"Unsupported file extension '{extension}' for file '{filename}'. "
                f"Supported extensions: {sorted(cls.SUPPORTED_EXTENSIONS)}"
            )

        return ValidationResult.success()

    @classmethod
    def validate_file_size(cls, size_bytes: int, filename: str = "") -> ValidationResult:
        """
        Validate that the file size is within the allowed limit.

        Args:
            size_bytes: File size in bytes
            filename: Optional filename for error message

        Returns:
            ValidationResult indicating success or failure with message
        """
        if size_bytes < 0:
            return ValidationResult.failure(
                f"Invalid file size: {size_bytes} bytes"
            )

        if size_bytes > cls.MAX_FILE_SIZE_BYTES:
            size_mb = size_bytes / (1024 * 1024)
            max_mb = cls.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            file_info = f" for file '{filename}'" if filename else ""
            return ValidationResult.failure(
                f"File size {size_mb:.2f}MB exceeds maximum allowed {max_mb:.0f}MB{file_info}"
            )

        return ValidationResult.success()

    @classmethod
    def validate_total_upload_size(
        cls, total_size_bytes: int
    ) -> ValidationResult:
        """
        Validate that the total upload size is within the allowed limit.

        Args:
            total_size_bytes: Total size of all files in bytes

        Returns:
            ValidationResult indicating success or failure with message
        """
        if total_size_bytes > cls.MAX_UPLOAD_SIZE_BYTES:
            size_mb = total_size_bytes / (1024 * 1024)
            max_mb = cls.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
            return ValidationResult.failure(
                f"Total upload size {size_mb:.2f}MB exceeds maximum allowed {max_mb:.0f}MB"
            )

        return ValidationResult.success()

    @classmethod
    def validate_file_count(cls, count: int) -> ValidationResult:
        """
        Validate that the number of files is within allowed range.

        Args:
            count: Number of files

        Returns:
            ValidationResult indicating success or failure with message
        """
        if count < cls.MIN_FILES_PER_UPLOAD:
            return ValidationResult.failure(
                f"At least {cls.MIN_FILES_PER_UPLOAD} file is required"
            )

        if count > cls.MAX_FILES_PER_UPLOAD:
            return ValidationResult.failure(
                f"Too many files: {count}. Maximum allowed is {cls.MAX_FILES_PER_UPLOAD} files"
            )

        return ValidationResult.success()

    @classmethod
    def is_binary_content(cls, content: bytes) -> bool:
        """
        Detect if content is binary (not text).

        Uses heuristics to detect binary content:
        1. Check for null bytes
        2. Check for non-printable characters

        Args:
            content: File content as bytes

        Returns:
            True if content appears to be binary, False if text
        """
        if not content:
            return False

        # Sample the content (for large files)
        sample = content[: cls.BINARY_SAMPLE_SIZE]

        # Count null bytes
        null_count = sample.count(b"\x00")
        if null_count > 0:
            # Any null byte in text file is suspicious
            null_ratio = null_count / len(sample)
            if null_ratio > cls.BINARY_NULL_THRESHOLD:
                return True
            # Even a few null bytes indicate binary
            if null_count > 2:
                return True

        # Try to decode as UTF-8
        try:
            sample.decode("utf-8")
            return False
        except UnicodeDecodeError:
            pass

        # Try to decode as other common encodings
        for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
            try:
                sample.decode(encoding)
                # Check for high concentration of control characters
                decoded = sample.decode(encoding)
                control_chars = sum(1 for c in decoded if ord(c) < 32 and c not in "\n\r\t")
                if control_chars / len(decoded) > 0.1:
                    return True
                return False
            except (UnicodeDecodeError, LookupError):
                continue

        return True

    @classmethod
    def validate_not_binary(
        cls, content: bytes, filename: str = ""
    ) -> ValidationResult:
        """
        Validate that the file content is not binary.

        Args:
            content: File content as bytes
            filename: Optional filename for error message

        Returns:
            ValidationResult indicating success or failure with message
        """
        if cls.is_binary_content(content):
            file_info = f" '{filename}'" if filename else ""
            return ValidationResult.failure(
                f"Binary files are not supported. File{file_info} appears to be binary."
            )

        return ValidationResult.success()

    @classmethod
    def validate_file(
        cls,
        filename: str,
        size_bytes: int,
        content: bytes | None = None,
    ) -> ValidationResult:
        """
        Validate a single file against all criteria.

        Args:
            filename: The filename
            size_bytes: File size in bytes
            content: Optional file content for binary detection

        Returns:
            ValidationResult indicating success or failure with message
        """
        # Validate extension
        result = cls.validate_extension(filename)
        if not result.is_valid:
            return result

        # Validate size
        result = cls.validate_file_size(size_bytes, filename)
        if not result.is_valid:
            return result

        # Validate not binary (if content provided)
        if content is not None:
            result = cls.validate_not_binary(content, filename)
            if not result.is_valid:
                return result

        return ValidationResult.success()

    @classmethod
    def validate_upload(
        cls,
        files: list[tuple[str, int, bytes | None]],
    ) -> ValidationResult:
        """
        Validate an entire upload (multiple files).

        Args:
            files: List of tuples (filename, size_bytes, content)
                   content can be None if binary detection not needed

        Returns:
            ValidationResult indicating success or failure with message
        """
        # Validate file count
        result = cls.validate_file_count(len(files))
        if not result.is_valid:
            return result

        # Validate total size
        total_size = sum(size for _, size, _ in files)
        result = cls.validate_total_upload_size(total_size)
        if not result.is_valid:
            return result

        # Validate each file
        for filename, size_bytes, content in files:
            result = cls.validate_file(filename, size_bytes, content)
            if not result.is_valid:
                return result

        return ValidationResult.success()

    @staticmethod
    def extract_extension(filename: str) -> str | None:
        """
        Extract file extension from filename.

        Args:
            filename: The filename to extract extension from

        Returns:
            The extension including the dot (e.g., '.py'), or None if no extension
        """
        if "." not in filename:
            return None

        # Handle files like .gitignore (no extension, just dot prefix)
        if filename.startswith(".") and filename.count(".") == 1:
            return None

        return "." + filename.rsplit(".", 1)[-1].lower()

    @staticmethod
    def get_mime_type(extension: str) -> str:
        """
        Get MIME type for a file extension.

        Args:
            extension: File extension including dot (e.g., '.py')

        Returns:
            MIME type string
        """
        mime_types = {
            ".py": "text/x-python",
            ".js": "application/javascript",
            ".ts": "application/typescript",
            ".jsx": "text/jsx",
            ".tsx": "text/tsx",
            ".html": "text/html",
            ".css": "text/css",
            ".java": "text/x-java-source",
            ".cpp": "text/x-c++src",
            ".c": "text/x-csrc",
            ".txt": "text/plain",
            ".md": "text/markdown",
        }
        return mime_types.get(extension.lower(), "application/octet-stream")
