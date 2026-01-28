"""
Document Queue Service - AI Code Learning Platform

This module provides the DocumentQueueService for managing document
generation queue operations including queuing, status tracking, and
queue position calculation.

Features:
- Queue document generation with duplicate prevention
- Calculate queue position and estimated wait time
- Check generation status
- Cancel pending generations

Usage:
    from src.services.document.document_queue_service import (
        DocumentQueueService,
        get_document_queue_service,
    )

    service = get_document_queue_service()
    celery_task_id = await service.queue_generation(task_id)
    position = await service.get_queue_position(task_id)
    estimated_time = await service.get_estimated_time(task_id)

Reference: spec.md FR-084 (informative loading states)
Task: T095 - Implement document generation queue with status tracking
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session_context
from src.models.learning_document import LearningDocument

logger = logging.getLogger(__name__)

# Average document generation time in seconds (3 minutes)
AVG_GENERATION_TIME_SECONDS = 180


class DocumentQueueError(Exception):
    """Base exception for document queue errors."""

    def __init__(self, message: str, task_id: uuid.UUID | None = None):
        super().__init__(message)
        self.task_id = task_id


class AlreadyInQueueError(DocumentQueueError):
    """Raised when trying to queue a document that's already queued."""

    pass


class NotInQueueError(DocumentQueueError):
    """Raised when trying to operate on a document not in queue."""

    pass


class DocumentQueueService:
    """
    Service for managing document generation queue operations.

    Handles queuing new document generations, tracking queue positions,
    and calculating estimated wait times.

    Attributes:
        avg_generation_time: Average time for document generation in seconds

    Example:
        service = DocumentQueueService()
        celery_task_id = await service.queue_generation(task_id)
        position = await service.get_queue_position(task_id)
        status = await service.get_generation_status(task_id)
    """

    def __init__(
        self,
        avg_generation_time: int = AVG_GENERATION_TIME_SECONDS,
    ):
        """
        Initialize DocumentQueueService.

        Args:
            avg_generation_time: Average generation time in seconds (default: 180)
        """
        self.avg_generation_time = avg_generation_time

    async def queue_generation(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> str:
        """
        Queue a document for generation.

        Creates a LearningDocument record with 'pending' status and
        queues the Celery task for background generation.

        Args:
            task_id: UUID of the task to generate document for
            session: Optional database session

        Returns:
            str: Celery task ID for tracking

        Raises:
            AlreadyInQueueError: If document is already being generated

        Example:
            celery_task_id = await service.queue_generation(task_id)
        """
        if session:
            return await self._queue_generation_with_session(task_id, session)

        async with get_session_context() as session:
            return await self._queue_generation_with_session(task_id, session)

    async def _queue_generation_with_session(
        self,
        task_id: uuid.UUID,
        session: AsyncSession,
    ) -> str:
        """Internal method to queue generation with a session."""
        # Check if document already exists
        stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            if existing.is_pending or existing.is_in_progress:
                raise AlreadyInQueueError(
                    f"Document generation already in progress for task {task_id}",
                    task_id,
                )
            if existing.is_completed:
                logger.info(f"Document already completed for task {task_id}")
                return existing.celery_task_id or ""

        # Create new document record or reset failed one
        if existing and existing.is_failed:
            # Reset failed document
            existing.generation_status = "pending"
            existing.generation_error = None
            existing.generation_started_at = None
            existing.generation_completed_at = None
            existing.content = {}
            document = existing
        else:
            # Create new document
            document = LearningDocument(
                task_id=task_id,
                generation_status="pending",
            )
            session.add(document)

        await session.flush()

        # Queue Celery task
        from src.tasks.document_generation import queue_document_generation

        celery_task_id = queue_document_generation(task_id)

        # Update document with celery_task_id
        document.celery_task_id = celery_task_id
        await session.commit()

        logger.info(
            f"Queued document generation for task {task_id} "
            f"(celery_task_id: {celery_task_id})"
        )

        return celery_task_id

    async def get_queue_position(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> int:
        """
        Get the queue position for a task's document generation.

        Returns 0 if currently generating, or the number of pending
        documents ahead in the queue.

        Args:
            task_id: UUID of the task
            session: Optional database session

        Returns:
            int: Queue position (0 = generating now, 1 = next, etc.)
                 Returns -1 if not in queue

        Example:
            position = await service.get_queue_position(task_id)
            if position == 0:
                print("Generating now")
            elif position > 0:
                print(f"{position} tasks ahead of you")
        """

        async def _get_position(session: AsyncSession) -> int:
            # Get the document for this task
            stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()

            if document is None:
                return -1

            if document.is_in_progress:
                return 0

            if document.is_completed or document.is_failed:
                return -1

            # Count pending documents created before this one
            stmt = (
                select(func.count())
                .select_from(LearningDocument)
                .where(
                    LearningDocument.generation_status == "pending",
                    LearningDocument.created_at < document.created_at,
                )
            )
            result = await session.execute(stmt)
            count = result.scalar() or 0

            # Add 1 for 1-based position (1 = first in queue)
            return count + 1

        if session:
            return await _get_position(session)

        async with get_session_context() as session:
            return await _get_position(session)

    async def get_estimated_time(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> int:
        """
        Get estimated time remaining for document generation in seconds.

        Calculates based on queue position and average generation time.

        Args:
            task_id: UUID of the task
            session: Optional database session

        Returns:
            int: Estimated seconds remaining (-1 if not in queue)

        Example:
            seconds = await service.get_estimated_time(task_id)
            minutes = seconds // 60
            print(f"Estimated wait: {minutes} minutes")
        """
        position = await self.get_queue_position(task_id, session)

        if position < 0:
            return -1

        if position == 0:
            # Currently generating - estimate based on start time
            async def _get_elapsed(session: AsyncSession) -> int:
                stmt = select(LearningDocument).where(
                    LearningDocument.task_id == task_id
                )
                result = await session.execute(stmt)
                document = result.scalar_one_or_none()

                if document and document.generation_started_at:
                    elapsed = (
                        datetime.now(UTC)
                        - document.generation_started_at.replace(tzinfo=UTC)
                    ).total_seconds()
                    remaining = max(0, self.avg_generation_time - int(elapsed))
                    return remaining
                return self.avg_generation_time

            if session:
                return await _get_elapsed(session)
            async with get_session_context() as session:
                return await _get_elapsed(session)

        # position * avg_time
        return position * self.avg_generation_time

    async def get_generation_status(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """
        Get comprehensive status information for document generation.

        Args:
            task_id: UUID of the task
            session: Optional database session

        Returns:
            dict: Status information including:
                - status: 'pending', 'in_progress', 'completed', 'failed', 'not_found'
                - queue_position: Position in queue (0 = generating)
                - estimated_time_remaining: Seconds until completion
                - started_at: Generation start timestamp
                - completed_at: Generation completion timestamp
                - error: Error message if failed
                - celery_task_id: Celery task ID

        Example:
            status = await service.get_generation_status(task_id)
            print(f"Status: {status['status']}")
            print(f"Wait time: {status['estimated_time_remaining']} seconds")
        """

        async def _get_status(session: AsyncSession) -> dict[str, Any]:
            stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()

            if document is None:
                return {
                    "status": "not_found",
                    "task_id": str(task_id),
                    "queue_position": -1,
                    "estimated_time_remaining": -1,
                }

            queue_position = await self.get_queue_position(task_id, session)
            estimated_time = await self.get_estimated_time(task_id, session)

            return {
                "status": document.generation_status,
                "task_id": str(task_id),
                "document_id": str(document.id) if document.id else None,
                "queue_position": queue_position,
                "estimated_time_remaining": estimated_time,
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
                "error": document.generation_error,
                "celery_task_id": document.celery_task_id,
                "has_content": document.has_content,
            }

        if session:
            return await _get_status(session)

        async with get_session_context() as session:
            return await _get_status(session)

    async def is_generation_in_progress(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> bool:
        """
        Check if document generation is currently in progress.

        Args:
            task_id: UUID of the task
            session: Optional database session

        Returns:
            bool: True if pending or in_progress

        Example:
            if await service.is_generation_in_progress(task_id):
                print("Please wait for generation to complete")
        """

        async def _check_in_progress(session: AsyncSession) -> bool:
            stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()

            if document is None:
                return False

            return document.is_pending or document.is_in_progress

        if session:
            return await _check_in_progress(session)

        async with get_session_context() as session:
            return await _check_in_progress(session)

    async def cancel_generation(
        self,
        task_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> bool:
        """
        Cancel a pending document generation.

        Only works for pending documents - cannot cancel in_progress.

        Args:
            task_id: UUID of the task
            session: Optional database session

        Returns:
            bool: True if cancelled successfully

        Raises:
            NotInQueueError: If document is not pending

        Example:
            if await service.cancel_generation(task_id):
                print("Generation cancelled")
        """

        async def _cancel(session: AsyncSession) -> bool:
            stmt = select(LearningDocument).where(LearningDocument.task_id == task_id)
            result = await session.execute(stmt)
            document = result.scalar_one_or_none()

            if document is None:
                raise NotInQueueError(
                    f"No document found for task {task_id}",
                    task_id,
                )

            if not document.is_pending:
                raise NotInQueueError(
                    f"Cannot cancel - document is {document.generation_status}",
                    task_id,
                )

            # Mark as failed with cancellation message
            document.generation_status = "failed"
            document.generation_error = "Cancelled by user"
            document.generation_completed_at = datetime.now(UTC)

            # Revoke Celery task if exists
            if document.celery_task_id:
                try:
                    from src.tasks.celery_app import celery_app

                    celery_app.control.revoke(
                        document.celery_task_id,
                        terminate=False,
                    )
                except Exception as e:
                    logger.warning(f"Failed to revoke Celery task: {e}")

            await session.commit()
            logger.info(f"Cancelled document generation for task {task_id}")
            return True

        if session:
            return await _cancel(session)

        async with get_session_context() as session:
            return await _cancel(session)


def get_document_queue_service(
    avg_generation_time: int = AVG_GENERATION_TIME_SECONDS,
) -> DocumentQueueService:
    """
    Factory function to create a DocumentQueueService.

    Args:
        avg_generation_time: Average generation time in seconds

    Returns:
        DocumentQueueService: Configured service instance
    """
    return DocumentQueueService(avg_generation_time=avg_generation_time)


__all__ = [
    "DocumentQueueService",
    "DocumentQueueError",
    "AlreadyInQueueError",
    "NotInQueueError",
    "get_document_queue_service",
    "AVG_GENERATION_TIME_SECONDS",
]
