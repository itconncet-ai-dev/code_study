"""
Unit tests for Celery Application Configuration - AI Code Learning Platform

Tests cover:
- CelerySettings configuration and validation
- URL construction from individual settings
- Celery app configuration
- Task queue and routing configuration
"""

import pytest

from src.tasks.celery_app import (
    CelerySettings,
    create_celery_app,
    get_celery_settings,
)


class TestCelerySettings:
    """Tests for CelerySettings configuration."""

    def test_default_settings(self):
        """Test default Celery settings are loaded with sensible defaults."""
        settings = CelerySettings(
            # Override to avoid loading from .env during tests
            _env_file=None,
        )

        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379
        assert settings.redis_password == ""
        assert settings.celery_task_time_limit == 300
        assert settings.celery_result_expires == 86400
        assert settings.celery_task_acks_late is True
        assert settings.celery_worker_prefetch_multiplier == 1

    def test_broker_url_construction_without_password(self):
        """Test broker URL is constructed correctly without password."""
        settings = CelerySettings(
            redis_host="localhost",
            redis_port=6379,
            redis_password="",
            celery_broker_url=None,
            _env_file=None,
        )

        assert settings.broker_url == "redis://localhost:6379/1"

    def test_broker_url_construction_with_password(self):
        """Test broker URL is constructed correctly with password."""
        settings = CelerySettings(
            redis_host="redis.example.com",
            redis_port=6380,
            redis_password="secret123",
            celery_broker_url=None,
            _env_file=None,
        )

        assert settings.broker_url == "redis://:secret123@redis.example.com:6380/1"

    def test_broker_url_from_env_variable(self):
        """Test broker URL uses explicit CELERY_BROKER_URL when set."""
        settings = CelerySettings(
            celery_broker_url="redis://custom-host:6379/5",
            _env_file=None,
        )

        assert settings.broker_url == "redis://custom-host:6379/5"

    def test_result_backend_url_construction_without_password(self):
        """Test result backend URL is constructed correctly without password."""
        settings = CelerySettings(
            redis_host="localhost",
            redis_port=6379,
            redis_password="",
            celery_result_backend=None,
            _env_file=None,
        )

        assert settings.result_backend_url == "redis://localhost:6379/2"

    def test_result_backend_url_construction_with_password(self):
        """Test result backend URL is constructed correctly with password."""
        settings = CelerySettings(
            redis_host="redis.example.com",
            redis_port=6380,
            redis_password="secret123",
            celery_result_backend=None,
            _env_file=None,
        )

        assert (
            settings.result_backend_url == "redis://:secret123@redis.example.com:6380/2"
        )

    def test_result_backend_url_from_env_variable(self):
        """Test result backend URL uses explicit CELERY_RESULT_BACKEND when set."""
        settings = CelerySettings(
            celery_result_backend="redis://custom-host:6379/10",
            _env_file=None,
        )

        assert settings.result_backend_url == "redis://custom-host:6379/10"

    def test_is_development(self):
        """Test is_development computed property."""
        dev_settings = CelerySettings(app_env="development", _env_file=None)
        prod_settings = CelerySettings(app_env="production", _env_file=None)

        assert dev_settings.is_development is True
        assert dev_settings.is_production is False
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True

    def test_task_time_limit_validation(self):
        """Test task time limit has valid range."""
        settings = CelerySettings(celery_task_time_limit=600, _env_file=None)
        assert settings.celery_task_time_limit == 600

    def test_different_redis_databases_for_broker_and_backend(self):
        """Test broker uses db 1 and backend uses db 2 by default."""
        settings = CelerySettings(
            redis_host="localhost",
            redis_port=6379,
            celery_broker_url=None,
            celery_result_backend=None,
            _env_file=None,
        )

        # Broker should use database 1
        assert "/1" in settings.broker_url
        # Backend should use database 2
        assert "/2" in settings.result_backend_url


class TestCeleryAppConfiguration:
    """Tests for Celery app configuration."""

    @pytest.fixture
    def celery_app(self):
        """Create a Celery app for testing."""
        return create_celery_app()

    def test_celery_app_created(self, celery_app):
        """Test Celery app is created successfully."""
        assert celery_app is not None
        assert celery_app.main == "code_learning_tasks"

    def test_celery_app_broker_configured(self, celery_app):  # noqa: ARG002
        """Test Celery app has broker URL configured."""
        settings = get_celery_settings()
        # The broker URL should contain redis://
        assert "redis://" in settings.broker_url

    def test_celery_app_serializer_config(self, celery_app):
        """Test Celery app uses JSON serialization."""
        assert celery_app.conf.task_serializer == "json"
        assert "json" in celery_app.conf.accept_content
        assert celery_app.conf.result_serializer == "json"

    def test_celery_app_timezone_config(self, celery_app):
        """Test Celery app uses UTC timezone."""
        assert celery_app.conf.timezone == "UTC"
        assert celery_app.conf.enable_utc is True

    def test_celery_app_task_time_limit(self, celery_app):
        """Test Celery app has task time limits configured."""
        settings = get_celery_settings()
        assert celery_app.conf.task_time_limit == settings.celery_task_time_limit
        # Soft limit should be 30 seconds less than hard limit
        assert (
            celery_app.conf.task_soft_time_limit == settings.celery_task_time_limit - 30
        )

    def test_celery_app_result_expiration(self, celery_app):
        """Test Celery app has result expiration configured."""
        settings = get_celery_settings()
        assert celery_app.conf.result_expires == settings.celery_result_expires

    def test_celery_app_task_queues_configured(self, celery_app):
        """Test Celery app has task queues configured."""
        queues = celery_app.conf.task_queues
        assert "default" in queues
        assert "document_generation" in queues
        assert "practice_generation" in queues
        assert "cleanup" in queues

    def test_celery_app_task_routes_configured(self, celery_app):
        """Test Celery app has task routes configured."""
        routes = celery_app.conf.task_routes
        assert "src.tasks.document_generation.*" in routes
        assert "src.tasks.practice_generation.*" in routes
        assert "src.tasks.trash_cleanup.*" in routes

    def test_celery_app_worker_settings(self, celery_app):
        """Test Celery app has worker settings configured."""
        settings = get_celery_settings()
        assert (
            celery_app.conf.worker_prefetch_multiplier
            == settings.celery_worker_prefetch_multiplier
        )
        assert celery_app.conf.worker_max_tasks_per_child == 1000

    def test_celery_app_task_acknowledgement(self, celery_app):
        """Test Celery app has late acknowledgement configured."""
        assert celery_app.conf.task_acks_late is True
        assert celery_app.conf.task_reject_on_worker_lost is True

    def test_celery_app_task_tracking(self, celery_app):
        """Test Celery app tracks task started state."""
        assert celery_app.conf.task_track_started is True
        assert celery_app.conf.result_extended is True


class TestHealthCheckTask:
    """Tests for the health check task."""

    def test_health_check_task_registered(self):
        """Test health check task is registered in Celery app."""
        from src.tasks.celery_app import celery_app

        assert "src.tasks.celery_app.health_check" in celery_app.tasks


class TestGetCelerySettings:
    """Tests for get_celery_settings function."""

    def test_get_celery_settings_returns_instance(self):
        """Test get_celery_settings returns CelerySettings instance."""
        settings = get_celery_settings()
        assert isinstance(settings, CelerySettings)

    def test_get_celery_settings_cached(self):
        """Test get_celery_settings returns cached instance."""
        settings1 = get_celery_settings()
        settings2 = get_celery_settings()
        # Should be the exact same object due to lru_cache
        assert settings1 is settings2
