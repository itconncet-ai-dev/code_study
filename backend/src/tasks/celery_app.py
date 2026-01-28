"""
Celery Application Configuration - AI Code Learning Platform

This module provides the Celery application setup with Redis as both
the message broker and result backend. It handles async task processing
for CPU-intensive operations like AI document generation.

Features:
- Redis-based message broker and result backend
- Environment-based configuration with Pydantic
- Task time limits and retry policies
- Result expiration for memory management
- Proper serialization configuration

Usage:
    # Start Celery worker (from backend directory)
    celery -A src.tasks.celery_app worker --loglevel=info

    # Start Celery beat (for scheduled tasks)
    celery -A src.tasks.celery_app beat --loglevel=info

Environment Variables:
    CELERY_BROKER_URL: Redis URL for message broker
    CELERY_RESULT_BACKEND: Redis URL for result storage
    CELERY_TASK_TIME_LIMIT: Maximum task execution time in seconds
    REDIS_HOST: Redis server hostname
    REDIS_PORT: Redis server port
    REDIS_PASSWORD: Redis password (optional)
"""

from functools import lru_cache
from typing import Literal

from celery import Celery
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    """
    Celery configuration settings loaded from environment variables.

    All settings have sensible development defaults but should be
    explicitly configured in production environments.

    Environment Variables:
        CELERY_BROKER_URL: Redis URL for message broker (default: redis://localhost:6379/1)
        CELERY_RESULT_BACKEND: Redis URL for result storage (default: redis://localhost:6379/2)
        CELERY_TASK_TIME_LIMIT: Maximum task execution time in seconds
        REDIS_HOST: Redis server hostname
        REDIS_PORT: Redis server port
        REDIS_PASSWORD: Redis password (optional)
        APP_ENV: Application environment
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment mode
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment mode",
    )

    # Redis connection settings (used to construct URLs if not explicitly provided)
    redis_host: str = Field(
        default="localhost",
        description="Redis server hostname",
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis server port",
    )
    redis_password: str = Field(
        default="",
        description="Redis password (empty for no auth)",
    )

    # Celery broker URL (Redis)
    celery_broker_url: str | None = Field(
        default=None,
        description="Redis URL for Celery message broker",
    )

    # Celery result backend URL (Redis)
    celery_result_backend: str | None = Field(
        default=None,
        description="Redis URL for Celery result storage",
    )

    # Task execution settings
    celery_task_time_limit: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Maximum task execution time in seconds (default: 5 minutes)",
    )

    # Result expiration (24 hours default)
    celery_result_expires: int = Field(
        default=86400,
        ge=3600,
        le=604800,
        description="Result expiration time in seconds (default: 24 hours)",
    )

    # Task acknowledgement settings
    celery_task_acks_late: bool = Field(
        default=True,
        description="Acknowledge task after completion (not before)",
    )

    # Prefetch multiplier (how many tasks to prefetch)
    celery_worker_prefetch_multiplier: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of tasks to prefetch per worker",
    )

    @computed_field
    @property
    def broker_url(self) -> str:
        """
        Get the Celery broker URL.

        Returns CELERY_BROKER_URL if set, otherwise constructs from Redis settings.
        Uses Redis database 1 for broker by default.

        Returns:
            str: Redis URL for Celery broker
        """
        if self.celery_broker_url:
            return self.celery_broker_url

        # Construct from individual Redis settings
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/1"
        return f"redis://{self.redis_host}:{self.redis_port}/1"

    @computed_field
    @property
    def result_backend_url(self) -> str:
        """
        Get the Celery result backend URL.

        Returns CELERY_RESULT_BACKEND if set, otherwise constructs from Redis settings.
        Uses Redis database 2 for results by default.

        Returns:
            str: Redis URL for Celery result backend
        """
        if self.celery_result_backend:
            return self.celery_result_backend

        # Construct from individual Redis settings
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/2"
        return f"redis://{self.redis_host}:{self.redis_port}/2"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"


@lru_cache
def get_celery_settings() -> CelerySettings:
    """
    Get cached Celery settings instance.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance and consistency.

    Returns:
        CelerySettings: Cached settings instance
    """
    return CelerySettings()


def create_celery_app() -> Celery:
    """
    Create and configure the Celery application.

    Sets up the Celery app with Redis broker and backend,
    configures serialization, time limits, and retry policies.

    Returns:
        Celery: Configured Celery application instance
    """
    settings = get_celery_settings()

    # Create Celery app
    celery_app = Celery(
        "code_learning_tasks",
        broker=settings.broker_url,
        backend=settings.result_backend_url,
    )

    # Configure Celery
    celery_app.conf.update(
        # Task serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        # Timezone
        timezone="UTC",
        enable_utc=True,
        # Task execution limits
        task_time_limit=settings.celery_task_time_limit,
        task_soft_time_limit=settings.celery_task_time_limit - 30,  # Soft limit 30s before hard
        # Result management
        result_expires=settings.celery_result_expires,
        result_extended=True,  # Store additional task metadata
        # Task acknowledgement
        task_acks_late=settings.celery_task_acks_late,
        task_reject_on_worker_lost=True,  # Requeue if worker dies
        # Worker settings
        worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
        # Broker connection retry
        broker_connection_retry_on_startup=True,
        # Task routing (default queue)
        task_default_queue="default",
        # Task tracking
        task_track_started=True,
        # Prevent memory leaks with worker restarts
        worker_max_tasks_per_child=1000,
    )

    # Configure task queues for different priority levels
    celery_app.conf.task_queues = {
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "document_generation": {
            "exchange": "document_generation",
            "routing_key": "document_generation",
        },
        "practice_generation": {
            "exchange": "practice_generation",
            "routing_key": "practice_generation",
        },
        "cleanup": {
            "exchange": "cleanup",
            "routing_key": "cleanup",
        },
    }

    # Configure task routes
    celery_app.conf.task_routes = {
        "src.tasks.document_generation.*": {"queue": "document_generation"},
        "src.tasks.practice_generation.*": {"queue": "practice_generation"},
        "src.tasks.trash_cleanup.*": {"queue": "cleanup"},
    }

    # Auto-discover tasks from task modules
    celery_app.autodiscover_tasks(
        [
            "src.tasks",
        ]
    )

    return celery_app


# Create the Celery application instance
celery_app = create_celery_app()


# Expose app for Celery CLI
app = celery_app


def get_celery_app() -> Celery:
    """
    Get the Celery application instance.

    Returns:
        Celery: The configured Celery app instance
    """
    return celery_app


# Health check task for monitoring
@celery_app.task(bind=True, name="src.tasks.celery_app.health_check")
def health_check(self):
    """
    Health check task to verify Celery worker connectivity.

    Returns:
        dict: Status information including worker id and broker URL
    """
    settings = get_celery_settings()
    return {
        "status": "healthy",
        "worker_id": self.request.id,
        "environment": settings.app_env,
        "broker": settings.broker_url.split("@")[-1] if "@" in settings.broker_url else settings.broker_url,
    }
