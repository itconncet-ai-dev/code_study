"""
Document Services Package - Learning document generation and management.

This package provides services for generating and managing AI-powered
learning documents from uploaded code.

Modules:
    document_generation_service: Main service for document generation with retry logic
    document_queue_service: Queue management for async document generation

Usage:
    from src.services.document import (
        DocumentGenerationService,
        DocumentQueueService,
        get_document_generation_service,
        get_document_queue_service,
    )

    # Direct generation (sync context)
    service = get_document_generation_service()
    document = await service.generate_document(task_id)

    # Queue generation (async background)
    queue_service = get_document_queue_service()
    celery_task_id = await queue_service.queue_generation(task_id)
"""

from src.services.document.document_generation_service import (
    DocumentAlreadyExistsError,
    DocumentGenerationError,
    DocumentGenerationService,
    GenerationFailedError,
    NoCodeUploadedError,
    TaskNotFoundError,
    get_document_generation_service,
)
from src.services.document.document_queue_service import (
    AVG_GENERATION_TIME_SECONDS,
    AlreadyInQueueError,
    DocumentQueueError,
    DocumentQueueService,
    NotInQueueError,
    get_document_queue_service,
)

__all__ = [
    # Document Generation Service
    "DocumentGenerationService",
    "DocumentGenerationError",
    "TaskNotFoundError",
    "NoCodeUploadedError",
    "DocumentAlreadyExistsError",
    "GenerationFailedError",
    "get_document_generation_service",
    # Document Queue Service
    "DocumentQueueService",
    "DocumentQueueError",
    "AlreadyInQueueError",
    "NotInQueueError",
    "get_document_queue_service",
    "AVG_GENERATION_TIME_SECONDS",
]
