"""
Tasks Package - Celery background tasks for async operations.

This package contains:
- celery_app: Celery application configuration with Redis broker/backend
- test_tasks: Test tasks for verifying Celery/Redis connectivity
- document_generation: Async document generation with AI

Usage:
    from src.tasks import celery_app, generate_document_task

    # Start worker
    celery -A src.tasks.celery_app worker --loglevel=info

    # Queue document generation
    from src.tasks import queue_document_generation
    celery_task_id = queue_document_generation(task_id)
"""

from .celery_app import celery_app, get_celery_app, get_celery_settings
from .document_generation import (
    generate_document_task,
    queue_document_generation,
)
from .test_tasks import quick_test, simulate_document_generation

__all__ = [
    "celery_app",
    "get_celery_app",
    "get_celery_settings",
    "quick_test",
    "simulate_document_generation",
    "generate_document_task",
    "queue_document_generation",
]
