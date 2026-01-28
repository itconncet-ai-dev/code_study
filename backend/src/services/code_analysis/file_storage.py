"""
File Storage Service - AI Code Learning Platform

This module provides file storage utilities for uploaded code files.
Handles saving, reading, and deleting files in the storage directory.

Storage Structure:
    storage/uploads/{user_id}/{task_id}/{uuid}.{ext}

Reference: T067 - Implement file storage service
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import BinaryIO

import aiofiles
import aiofiles.os


class FileStorageService:
    """
    Service for managing file storage operations.

    Handles file persistence in the filesystem with organized directory
    structure based on user and task IDs.
    """

    # Base storage directory (relative to project root)
    STORAGE_ROOT = Path("storage/uploads")

    @classmethod
    def generate_storage_path(
        cls,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        filename: str,
    ) -> str:
        """
        Generate storage path for a file.

        Args:
            user_id: User UUID
            task_id: Task UUID
            filename: Original filename (extension will be preserved)

        Returns:
            str: Storage path in format "storage/uploads/{user_id}/{task_id}/{uuid}.{ext}"
        """
        # Generate unique filename preserving extension
        extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{extension}"

        # Build path: storage/uploads/{user_id}/{task_id}/{uuid}.{ext}
        storage_path = cls.STORAGE_ROOT / str(user_id) / str(task_id) / unique_filename

        return str(storage_path)

    @classmethod
    async def save_file(
        cls,
        content: bytes,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        filename: str,
    ) -> str:
        """
        Save file content to storage.

        Creates directories if they don't exist. Returns the storage path.

        Args:
            content: File content as bytes
            user_id: User UUID
            task_id: Task UUID
            filename: Original filename (for extension)

        Returns:
            str: Storage path where file was saved

        Raises:
            OSError: If file write fails
        """
        # Generate storage path
        storage_path = cls.generate_storage_path(user_id, task_id, filename)
        file_path = Path(storage_path)

        # Create directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return storage_path

    @classmethod
    async def read_file(cls, storage_path: str) -> bytes:
        """
        Read file content from storage.

        Args:
            storage_path: Path to the stored file

        Returns:
            bytes: File content

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If file read fails
        """
        file_path = Path(storage_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        return content

    @classmethod
    async def delete_file(cls, storage_path: str) -> None:
        """
        Delete file from storage.

        Silently succeeds if file doesn't exist.

        Args:
            storage_path: Path to the stored file

        Raises:
            OSError: If file deletion fails
        """
        file_path = Path(storage_path)

        if file_path.exists():
            await aiofiles.os.remove(file_path)

    @classmethod
    async def delete_task_files(cls, user_id: uuid.UUID, task_id: uuid.UUID) -> None:
        """
        Delete all files for a task.

        Removes the entire task directory and its contents.

        Args:
            user_id: User UUID
            task_id: Task UUID

        Raises:
            OSError: If directory deletion fails
        """
        task_dir = cls.STORAGE_ROOT / str(user_id) / str(task_id)

        if task_dir.exists() and task_dir.is_dir():
            # Delete all files in the directory
            for file_path in task_dir.iterdir():
                if file_path.is_file():
                    await aiofiles.os.remove(file_path)

            # Remove the directory itself
            await aiofiles.os.rmdir(task_dir)

    @classmethod
    async def file_exists(cls, storage_path: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            storage_path: Path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        return Path(storage_path).exists()


__all__ = ["FileStorageService"]
