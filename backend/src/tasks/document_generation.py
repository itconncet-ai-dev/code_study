"""
Document Generation Celery Tasks - AI Code Learning Platform

This module provides Celery tasks for asynchronous document generation.
Documents are generated in the background while users can continue using
the application.

Features:
- Async document generation with Celery
- Automatic retry on transient failures
- Status tracking in database
- Exponential backoff for retries

Usage:
    from src.tasks.document_generation import generate_document_task

    # Queue document generation (returns immediately)
    result = generate_document_task.delay(str(task_id))

    # Check status
    if result.ready():
        document_data = result.get()

Reference: spec.md FR-083 (document generation within 3 minutes)
Task: T094 - Implement Celery task for async document generation
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

from celery import Task as CeleryTask
from celery.exceptions import MaxRetriesExceededError

from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


class DocumentGenerationTask(CeleryTask):
    """
    Custom Celery task class for document generation.

    Provides lifecycle hooks for logging and error handling.
    """

    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """Called when task succeeds."""
        logger.info(f"Document generation task {task_id} completed successfully")

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Called when task fails after all retries."""
        logger.error(f"Document generation task {task_id} failed: {exc}")

    def on_retry(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Called when task is retried."""
        logger.warning(f"Document generation task {task_id} retrying: {exc}")


@celery_app.task(
    bind=True,
    base=DocumentGenerationTask,
    name="src.tasks.document_generation.generate_document_task",
    queue="document_generation",
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True,
    time_limit=300,  # 5 minutes hard limit
    soft_time_limit=270,  # 4.5 minutes soft limit
)
def generate_document_task(self, task_id: str) -> dict[str, Any]:
    """
    Celery task for generating a learning document.

    This task wraps the async DocumentGenerationService and runs it
    in the Celery worker's sync environment.

    Args:
        task_id: UUID string of the task to generate document for

    Returns:
        dict: Result containing document_id, status, and generation time

    Raises:
        MaxRetriesExceededError: If all retries are exhausted

    Example:
        # Queue task
        result = generate_document_task.delay("uuid-string")

        # Wait for result (blocking)
        document_data = result.get(timeout=300)
    """
    celery_task_id = self.request.id
    logger.info(
        f"Starting document generation for task {task_id} "
        f"(celery_task_id: {celery_task_id})"
    )

    try:
        # Run the async generation in sync context
        result = asyncio.run(
            _generate_document_async(task_id, celery_task_id)
        )
        return result

    except Exception as exc:
        logger.error(
            f"Document generation failed for task {task_id}: "
            f"{type(exc).__name__}: {str(exc)}"
        )

        # Mark as failed in database before retry
        try:
            asyncio.run(_mark_generation_failed(task_id, str(exc)))
        except Exception as db_err:
            logger.error(f"Failed to mark generation as failed: {db_err}")

        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error(
                f"Document generation exhausted all retries for task {task_id}"
            )
            raise


async def _generate_document_async(
    task_id: str,
    celery_task_id: str,
) -> dict[str, Any]:
    """
    Async helper function to generate document.

    This function is called from the sync Celery task and handles
    the actual document generation using DocumentGenerationService.

    Args:
        task_id: UUID string of the task
        celery_task_id: Celery task ID for tracking

    Returns:
        dict: Result with document_id, status, and duration
    """
    from src.services.document.document_generation_service import (
        DocumentGenerationService,
        DocumentGenerationError,
    )

    task_uuid = uuid.UUID(task_id)
    service = DocumentGenerationService()

    try:
        document = await service.generate_document(
            task_id=task_uuid,
            celery_task_id=celery_task_id,
        )

        return {
            "status": "completed",
            "document_id": str(document.id),
            "task_id": task_id,
            "duration_seconds": document.generation_duration_seconds,
            "has_content": document.has_content,
        }

    except DocumentGenerationError as e:
        logger.error(f"Document generation error: {e}")
        raise


async def _mark_generation_failed(task_id: str, error_message: str) -> None:
    """
    Mark document generation as failed in database.

    This is called before retry to update the status so users
    can see that generation is being retried.

    Args:
        task_id: UUID string of the task
        error_message: Error description
    """
    from sqlalchemy import select, update

    from src.db.session import get_session_context
    from src.models.learning_document import LearningDocument

    task_uuid = uuid.UUID(task_id)

    async with get_session_context() as session:
        # Update status to failed
        stmt = (
            update(LearningDocument)
            .where(LearningDocument.task_id == task_uuid)
            .values(
                generation_status="failed",
                generation_error=f"Retrying: {error_message}",
            )
        )
        await session.execute(stmt)
        await session.commit()


# Convenience function for direct calling
def queue_document_generation(task_id: uuid.UUID | str) -> str:
    """
    Queue a document generation task.

    This is a convenience function that can be called from anywhere
    to queue document generation.

    Args:
        task_id: UUID of the task (string or UUID object)

    Returns:
        str: Celery task ID for tracking

    Example:
        celery_task_id = queue_document_generation(task.id)
    """
    if isinstance(task_id, uuid.UUID):
        task_id = str(task_id)

    result = generate_document_task.delay(task_id)
    logger.info(f"Queued document generation for task {task_id}: {result.id}")

    return result.id


__all__ = [
    "generate_document_task",
    "queue_document_generation",
    "DocumentGenerationTask",
]
