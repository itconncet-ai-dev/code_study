"""
Document Generation Service - AI Code Learning Platform

This module provides the DocumentGenerationService for generating 7-chapter
learning documents from uploaded code using AI (Gemini/OpenRouter).

Features:
- Async document generation from task code
- Retry logic for transient AI API failures
- Database integration for status tracking
- File content aggregation from code files
- Validation of generated content structure

Usage:
    from src.services.document.document_generation_service import (
        DocumentGenerationService,
        get_document_generation_service,
    )

    service = get_document_generation_service()
    document = await service.generate_document(task_id)

Reference: spec.md FR-026 through FR-039 (Learning Document Generation)
Task: T093 - Implement DocumentGenerationService with retry logic
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.session import get_session_context
from src.models.learning_document import LearningDocument
from src.models.task import Task
from src.models.uploaded_code import UploadedCode
from src.services.ai.prompts import (
    FileInfo,
    get_document_generation_prompt,
    get_system_instruction,
    validate_document_structure,
)
from src.services.ai.provider import get_ai_client, get_ai_error_classes
from src.services.code_analysis.file_storage import FileStorageService

logger = logging.getLogger(__name__)


class DocumentGenerationError(Exception):
    """Base exception for document generation errors."""

    def __init__(self, message: str, task_id: uuid.UUID | None = None):
        super().__init__(message)
        self.task_id = task_id


class TaskNotFoundError(DocumentGenerationError):
    """Raised when task is not found."""

    pass


class NoCodeUploadedError(DocumentGenerationError):
    """Raised when task has no uploaded code."""

    pass


class DocumentAlreadyExistsError(DocumentGenerationError):
    """Raised when a completed document already exists for the task."""

    pass


class GenerationFailedError(DocumentGenerationError):
    """Raised when AI generation fails after all retries."""

    def __init__(
        self,
        message: str,
        task_id: uuid.UUID | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message, task_id)
        self.original_error = original_error


class DocumentGenerationService:
    """
    Service for generating AI-powered learning documents from uploaded code.

    This service handles the complete document generation workflow:
    1. Fetches task and code files from database
    2. Reads code content from file storage
    3. Builds prompts using the prompts module
    4. Calls AI service with retry logic
    5. Validates and saves the generated document

    Attributes:
        max_retries: Maximum retry attempts for AI API failures (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 2.0)
        retry_multiplier: Exponential backoff multiplier (default: 2.0)
        max_retry_delay: Maximum delay between retries (default: 30.0)

    Example:
        service = DocumentGenerationService()

        # Generate document for a task
        try:
            document = await service.generate_document(task_id)
            print(f"Generated document with {len(document.content)} chapters")
        except DocumentGenerationError as e:
            print(f"Generation failed: {e}")
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        retry_multiplier: float = 2.0,
        max_retry_delay: float = 30.0,
    ):
        """
        Initialize DocumentGenerationService.

        Args:
            max_retries: Maximum retry attempts for AI failures
            retry_delay: Initial delay between retries (seconds)
            retry_multiplier: Multiplier for exponential backoff
            max_retry_delay: Maximum delay between retries (seconds)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.max_retry_delay = max_retry_delay

    async def generate_document(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
        celery_task_id: str | None = None,
        force_regenerate: bool = False,
    ) -> LearningDocument:
        """
        Generate a learning document for a task.

        This is the main entry point for document generation. It handles:
        - Fetching the task and its code files
        - Checking for existing documents
        - Creating/updating document status
        - Generating content via AI
        - Saving the completed document

        Args:
            task_id: UUID of the task to generate document for
            session: Optional database session (creates one if not provided)
            celery_task_id: Optional Celery task ID for async tracking
            force_regenerate: If True, regenerate even if document exists

        Returns:
            LearningDocument: The generated document

        Raises:
            TaskNotFoundError: If task doesn't exist
            NoCodeUploadedError: If task has no code
            DocumentAlreadyExistsError: If document exists and force_regenerate=False
            GenerationFailedError: If AI generation fails after retries
        """
        if session:
            return await self._generate_document_with_session(
                task_id, session, celery_task_id, force_regenerate
            )

        async with get_session_context() as session:
            return await self._generate_document_with_session(
                task_id, session, celery_task_id, force_regenerate
            )

    async def _generate_document_with_session(
        self,
        task_id: uuid.UUID,
        session: AsyncSession,
        celery_task_id: str | None,
        force_regenerate: bool,
    ) -> LearningDocument:
        """Internal method that handles document generation with a session."""
        logger.info(f"Starting document generation for task {task_id}")

        # 1. Fetch task with related data
        task = await self._get_task_with_code(session, task_id)

        # 2. Check for existing document
        document = await self._get_or_create_document(
            session, task, celery_task_id, force_regenerate
        )

        # 3. Mark as in_progress
        document.start_generation(celery_task_id or str(uuid.uuid4()))
        await session.flush()

        try:
            # 4. Get code content
            code_content, language, files_info = await self._get_code_content(task)

            # 5. Generate document content with retry
            content = await self._generate_with_retry(
                code_content, language, files_info, task_id
            )

            # 6. Validate and save
            is_valid, errors = validate_document_structure(content)
            if not is_valid:
                raise GenerationFailedError(
                    f"Generated content failed validation: {errors}",
                    task_id=task_id,
                )

            document.complete_generation(content)
            await session.flush()

            logger.info(
                f"Document generation completed for task {task_id} "
                f"in {document.generation_duration_seconds:.2f}s"
            )

            return document

        except GenerationFailedError:
            raise
        except Exception as e:
            error_msg = f"Document generation failed: {type(e).__name__}: {str(e)}"
            logger.error(f"Task {task_id}: {error_msg}")
            document.fail_generation(error_msg)
            await session.flush()
            raise GenerationFailedError(error_msg, task_id, e)

    async def _get_task_with_code(
        self,
        session: AsyncSession,
        task_id: uuid.UUID,
    ) -> Task:
        """
        Fetch task with uploaded code and files.

        Args:
            session: Database session
            task_id: Task UUID

        Returns:
            Task: Task with loaded relationships

        Raises:
            TaskNotFoundError: If task doesn't exist
            NoCodeUploadedError: If task has no uploaded code
        """
        stmt = (
            select(Task)
            .options(
                selectinload(Task.uploaded_code).selectinload(UploadedCode.code_files),
                selectinload(Task.learning_document),
            )
            .where(Task.id == task_id)
            .where(Task.deletion_status == "active")
        )

        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if task is None:
            raise TaskNotFoundError(f"Task not found: {task_id}", task_id)

        if task.uploaded_code is None or not task.uploaded_code.code_files:
            raise NoCodeUploadedError(f"Task has no uploaded code: {task_id}", task_id)

        return task

    async def _get_or_create_document(
        self,
        session: AsyncSession,
        task: Task,
        _celery_task_id: str | None,
        force_regenerate: bool,
    ) -> LearningDocument:
        """
        Get existing document or create a new one.

        Args:
            session: Database session
            task: Task entity
            celery_task_id: Optional Celery task ID
            force_regenerate: If True, reset existing document

        Returns:
            LearningDocument: New or existing document

        Raises:
            DocumentAlreadyExistsError: If completed document exists and not forcing
        """
        if task.learning_document:
            document = task.learning_document

            if document.is_completed and not force_regenerate:
                raise DocumentAlreadyExistsError(
                    f"Document already exists for task: {task.id}",
                    task.id,
                )

            if document.is_in_progress:
                logger.warning(
                    f"Document generation already in progress for task {task.id}"
                )

            # Reset for regeneration
            document.generation_status = "pending"
            document.content = {}
            document.generation_error = None
            document.generation_started_at = None
            document.generation_completed_at = None
            return document

        # Create new document
        document = LearningDocument(
            task_id=task.id,
            generation_status="pending",
        )
        session.add(document)
        await session.flush()

        return document

    async def _get_code_content(
        self,
        task: Task,
    ) -> tuple[str, str, list[FileInfo]]:
        """
        Get aggregated code content from task's files.

        Reads all code files and combines them with file headers.

        Args:
            task: Task with loaded code files

        Returns:
            tuple: (combined_code, detected_language, files_info)
        """
        uploaded_code = task.uploaded_code
        code_files = uploaded_code.code_files

        files_info: list[FileInfo] = []
        code_parts: list[str] = []

        for code_file in code_files:
            try:
                # Try reading from database first (for distributed workers),
                # fall back to filesystem
                if code_file.content:
                    content = code_file.content
                else:
                    content_bytes = await FileStorageService.read_file(
                        code_file.storage_path
                    )
                    content = content_bytes.decode("utf-8", errors="replace")

                # Add file header for multi-file uploads
                if len(code_files) > 1:
                    file_path = code_file.file_path or code_file.file_name
                    code_parts.append(f"# === File: {file_path} ===")

                code_parts.append(content)

                files_info.append(
                    FileInfo(
                        file_name=code_file.file_name,
                        file_path=code_file.file_path,
                        content=content,
                        language=uploaded_code.detected_language or "text",
                    )
                )
            except FileNotFoundError:
                logger.warning(f"File not found: {code_file.storage_path}, skipping")
                continue

        if not code_parts:
            raise NoCodeUploadedError(
                f"No readable code files for task: {task.id}",
                task.id,
            )

        combined_code = "\n\n".join(code_parts)
        language = uploaded_code.detected_language or "text"

        return combined_code, language, files_info

    async def _generate_with_retry(
        self,
        code: str,
        language: str,
        files_info: list[FileInfo],
        task_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Generate document content with retry logic.

        Uses exponential backoff for transient failures.

        Args:
            code: Combined code content
            language: Detected programming language
            files_info: List of file information
            task_id: Task UUID for error context

        Returns:
            dict: Generated document content with 7 chapters

        Raises:
            GenerationFailedError: If all retries fail
        """
        # Build prompt
        prompt = get_document_generation_prompt(code, language, files_info)
        system_instruction = get_system_instruction()

        # Get AI client and error classes
        client = get_ai_client()
        error_classes = get_ai_error_classes()

        last_error: Exception | None = None
        delay = self.retry_delay

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    f"Task {task_id}: AI generation attempt "
                    f"{attempt + 1}/{self.max_retries + 1}"
                )

                content = await client.generate_json(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=0.5,
                    timeout=180,  # 3 minutes for document generation
                )

                return content

            except error_classes["rate_limit"] as e:
                last_error = e
                logger.warning(
                    f"Task {task_id}: Rate limit hit (attempt {attempt + 1})"
                )
                if attempt < self.max_retries:
                    await self._wait_with_backoff(delay * 2, attempt)
                    delay = min(delay * self.retry_multiplier, self.max_retry_delay)

            except error_classes["timeout"] as e:
                last_error = e
                logger.warning(f"Task {task_id}: Timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(delay * self.retry_multiplier, self.max_retry_delay)

            except error_classes["content_blocked"] as e:
                # Don't retry content blocks - it won't change
                logger.error(f"Task {task_id}: Content blocked by safety filter")
                raise GenerationFailedError(
                    f"Content blocked by safety filter: {str(e)}",
                    task_id,
                    e,
                )

            except error_classes["api"] as e:
                last_error = e
                logger.warning(
                    f"Task {task_id}: API error (attempt {attempt + 1}): {str(e)}"
                )
                if attempt < self.max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(delay * self.retry_multiplier, self.max_retry_delay)

            except Exception as e:
                last_error = e
                logger.error(
                    f"Task {task_id}: Unexpected error: {type(e).__name__}: {str(e)}"
                )
                if attempt < self.max_retries:
                    await self._wait_with_backoff(delay, attempt)
                    delay = min(delay * self.retry_multiplier, self.max_retry_delay)

        # All retries exhausted
        raise GenerationFailedError(
            f"Document generation failed after {self.max_retries + 1} attempts: "
            f"{str(last_error)}",
            task_id,
            last_error,
        )

    async def _wait_with_backoff(self, delay: float, attempt: int) -> None:
        """Wait with exponential backoff before retry."""
        logger.info(f"Retrying in {delay:.1f}s (attempt {attempt + 1})...")
        await asyncio.sleep(delay)

    async def get_document_status(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """
        Get the current status of document generation.

        Args:
            task_id: Task UUID
            session: Optional database session

        Returns:
            dict: Status information including:
                - status: 'pending', 'in_progress', 'completed', 'failed', 'not_found'
                - celery_task_id: Celery task ID if available
                - started_at: Generation start time
                - completed_at: Generation completion time
                - error: Error message if failed
                - has_content: Whether document has content
        """

        async def _get_status(session: AsyncSession) -> dict[str, Any]:
            stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()

            if document is None:
                return {"status": "not_found", "task_id": str(task_id)}

            return {
                "status": document.generation_status,
                "task_id": str(task_id),
                "document_id": str(document.id),
                "celery_task_id": document.celery_task_id,
                "started_at": (
                    document.generation_started_at.isoformat()
                    if document.generation_started_at
                    else None
                ),
                "completed_at": (
                    document.generation_completed_at.isoformat()
                    if document.generation_completed_at
                    else None
                ),
                "duration_seconds": document.generation_duration_seconds,
                "error": document.generation_error,
                "has_content": document.has_content,
            }

        if session:
            return await _get_status(session)

        async with get_session_context() as session:
            return await _get_status(session)

    async def get_document(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> LearningDocument | None:
        """
        Get the learning document for a task.

        Args:
            task_id: Task UUID
            session: Optional database session

        Returns:
            LearningDocument or None if not found
        """

        async def _get_document(session: AsyncSession) -> LearningDocument | None:
            stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        if session:
            return await _get_document(session)

        async with get_session_context() as session:
            return await _get_document(session)


def get_document_generation_service(
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> DocumentGenerationService:
    """
    Factory function to create a DocumentGenerationService.

    Args:
        max_retries: Maximum retry attempts
        retry_delay: Initial delay between retries

    Returns:
        DocumentGenerationService: Configured service instance
    """
    return DocumentGenerationService(
        max_retries=max_retries,
        retry_delay=retry_delay,
    )


__all__ = [
    "DocumentGenerationService",
    "DocumentGenerationError",
    "TaskNotFoundError",
    "NoCodeUploadedError",
    "DocumentAlreadyExistsError",
    "GenerationFailedError",
    "get_document_generation_service",
]
