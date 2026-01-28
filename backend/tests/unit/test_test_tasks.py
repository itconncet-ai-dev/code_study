"""
Unit tests for Test Tasks - Celery Integration Testing

Tests cover:
- Task registration in Celery app
- Task function signatures
- Basic task behavior (without actual Celery execution)
"""

import pytest

from src.tasks.test_tasks import (
    quick_test,
    simulate_document_generation,
)


class TestTaskRegistration:
    """Tests for task registration in Celery app."""

    def test_quick_test_task_registered(self):
        """Test quick_test task is registered in Celery app."""
        from src.tasks.celery_app import celery_app

        assert "src.tasks.test_tasks.quick_test" in celery_app.tasks

    def test_simulate_document_generation_task_registered(self):
        """Test simulate_document_generation task is registered in Celery app."""
        from src.tasks.celery_app import celery_app

        assert "src.tasks.test_tasks.simulate_document_generation" in celery_app.tasks


class TestQuickTestTask:
    """Tests for quick_test task behavior."""

    def test_quick_test_has_correct_name(self):
        """Test quick_test task has correct name."""
        assert quick_test.name == "src.tasks.test_tasks.quick_test"

    def test_quick_test_is_bound(self):
        """Test quick_test task is bound (has access to self)."""
        # Bound tasks have bind=True, which means first arg is 'self'
        assert hasattr(quick_test, "bind")


class TestSimulateDocumentGenerationTask:
    """Tests for simulate_document_generation task behavior."""

    def test_simulate_document_generation_has_correct_name(self):
        """Test simulate_document_generation task has correct name."""
        assert simulate_document_generation.name == "src.tasks.test_tasks.simulate_document_generation"

    def test_simulate_document_generation_is_bound(self):
        """Test simulate_document_generation task is bound (has access to self)."""
        assert hasattr(simulate_document_generation, "bind")


class TestTaskImports:
    """Tests for task imports from package."""

    def test_import_from_package(self):
        """Test tasks can be imported from tasks package."""
        from src.tasks import quick_test as qt
        from src.tasks import simulate_document_generation as sdg

        assert qt is quick_test
        assert sdg is simulate_document_generation
