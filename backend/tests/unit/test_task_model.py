"""
Unit Tests for Task SQLAlchemy Model - T061

TDD RED Phase: These tests define the expected behavior of the Task model.
All tests should FAIL initially until the model is implemented.

Test Coverage:
- UUID primary key generation
- project_id foreign key field
- task_number field (sequential within project, immutable)
- title field (required, min 5 characters)
- description field (optional, max 500 characters)
- upload_method field (enum: 'file', 'folder', 'paste')
- Timestamps (created_at, updated_at)
- Soft delete fields (deletion_status, trashed_at, scheduled_deletion_at)
- Project relationship (back_populates)

Reference: data-model.md §Task entity
"""

import uuid
from datetime import datetime, timedelta, timezone
import time

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


def unique_email(prefix: str) -> str:
    """Generate a unique email address for testing."""
    return f"{prefix}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}@example.com"


class TestTaskModel:
    """Test suite for Task SQLAlchemy model."""

    def test_task_model_exists(self):
        """Task model class should be importable from models package."""
        from src.models.task import Task

        assert Task is not None
        assert Task.__tablename__ == "tasks"

    def test_task_has_uuid_primary_key(self):
        """Task should have a UUID primary key field."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task Title"
        )

        assert task.id is not None
        assert isinstance(task.id, uuid.UUID)

    def test_task_project_id_required(self):
        """Task project_id field should be set."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.project_id == project_id
        assert isinstance(task.project_id, uuid.UUID)

    def test_task_number_field(self):
        """Task should have a task_number field."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Task Number Test"
        )

        assert task.task_number == 1

    def test_task_title_field(self):
        """Task should have a title field (min 5 characters)."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="My Learning Task"
        )

        assert task.title == "My Learning Task"

    def test_task_description_optional(self):
        """Task description field should be optional (nullable)."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.description is None

    def test_task_description_can_be_set(self):
        """Task description field should accept text."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task",
            description="This is a detailed task description."
        )

        assert task.description == "This is a detailed task description."

    def test_task_upload_method_field(self):
        """Task should have an upload_method field with valid values."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task",
            upload_method="file"
        )

        assert task.upload_method == "file"

    def test_task_upload_method_values(self):
        """Task upload_method should accept 'file', 'folder', 'paste'."""
        from src.models.task import Task

        project_id = uuid.uuid4()

        # Test each valid upload method
        for method in ["file", "folder", "paste"]:
            task = Task(
                project_id=project_id,
                task_number=1,
                title="Test Task",
                upload_method=method
            )
            assert task.upload_method == method

    def test_task_upload_method_nullable(self):
        """Task upload_method should be nullable (can be None)."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.upload_method is None

    def test_task_soft_delete_default(self):
        """Task deletion_status should default to 'active'."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.deletion_status == "active"

    def test_task_trashed_at_nullable(self):
        """Task trashed_at should be nullable by default."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.trashed_at is None

    def test_task_scheduled_deletion_at_nullable(self):
        """Task scheduled_deletion_at should be nullable by default."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.scheduled_deletion_at is None

    def test_task_has_timestamp_fields(self):
        """Task should have created_at and updated_at fields."""
        from src.models.task import Task

        columns = [col.name for col in Task.__table__.columns]

        assert "created_at" in columns
        assert "updated_at" in columns

    def test_task_model_table_columns(self):
        """Task model should have all expected columns per data-model.md."""
        from src.models.task import Task

        expected_columns = {
            "id",
            "project_id",
            "task_number",
            "title",
            "description",
            "upload_method",
            "created_at",
            "updated_at",
            "deletion_status",
            "trashed_at",
            "scheduled_deletion_at",
        }

        actual_columns = {col.name for col in Task.__table__.columns}

        assert expected_columns == actual_columns, (
            f"Missing columns: {expected_columns - actual_columns}, "
            f"Extra columns: {actual_columns - expected_columns}"
        )

    def test_task_soft_delete_can_be_set(self):
        """Task soft delete fields can be set for trashed state."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        trashed_time = datetime.now(timezone.utc)
        scheduled_time = trashed_time + timedelta(days=30)

        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task",
            deletion_status="trashed",
            trashed_at=trashed_time,
            scheduled_deletion_at=scheduled_time
        )

        assert task.deletion_status == "trashed"
        assert task.trashed_at == trashed_time
        assert task.scheduled_deletion_at == scheduled_time

    def test_task_soft_delete_method(self):
        """Task should have a soft_delete method."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        scheduled_deletion = datetime.now(timezone.utc) + timedelta(days=30)
        task.soft_delete(scheduled_deletion)

        assert task.deletion_status == "trashed"
        assert task.trashed_at is not None
        assert task.scheduled_deletion_at == scheduled_deletion

    def test_task_restore_method(self):
        """Task should have a restore method."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        trashed_time = datetime.now(timezone.utc)
        scheduled_time = trashed_time + timedelta(days=30)

        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task",
            deletion_status="trashed",
            trashed_at=trashed_time,
            scheduled_deletion_at=scheduled_time
        )

        task.restore()

        assert task.deletion_status == "active"
        assert task.trashed_at is None
        assert task.scheduled_deletion_at is None

    def test_task_is_trashed_property(self):
        """Task should have is_trashed property."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task",
            deletion_status="trashed"
        )

        assert task.is_trashed is True

    def test_task_is_active_property(self):
        """Task should have is_active property."""
        from src.models.task import Task

        project_id = uuid.uuid4()
        task = Task(
            project_id=project_id,
            task_number=1,
            title="Test Task"
        )

        assert task.is_active is True


@pytest.mark.asyncio
class TestTaskModelDatabase:
    """Database integration tests for Task model."""

    async def test_task_create_and_retrieve(self, db_session):
        """Task should be creatable and retrievable from database."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        # Create a user first
        user = User(
            email=unique_email("taskowner"),
            password_hash="$2b$12$test_hash_value"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create project for this user
        project = Project(
            user_id=user.id,
            title="Test Project"
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Create task for this project
        task = Task(
            project_id=project.id,
            task_number=1,
            title="Test Task Title",
            description="A test task description"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Verify persisted
        assert task.id is not None

        # Retrieve from database
        result = await db_session.execute(
            select(Task).where(Task.id == task.id)
        )
        retrieved_task = result.scalar_one()

        assert retrieved_task.title == "Test Task Title"
        assert retrieved_task.description == "A test task description"
        assert retrieved_task.project_id == project.id
        assert retrieved_task.task_number == 1
        assert retrieved_task.deletion_status == "active"

    async def test_task_project_id_foreign_key(self, db_session):
        """Task project_id should reference existing project."""
        from src.models.task import Task

        # Try to create task with non-existent project
        fake_project_id = uuid.uuid4()
        task = Task(
            project_id=fake_project_id,
            task_number=1,
            title="Orphan Task"
        )
        db_session.add(task)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_task_title_not_null_constraint(self, db_session):
        """Task title should have NOT NULL constraint."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("notitle_task"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        task = Task(project_id=project.id, task_number=1)
        db_session.add(task)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_task_timestamps_auto_set(self, db_session):
        """created_at and updated_at should be automatically set."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("task_timestamps"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(
            user_id=user.id,
            title="Timestamp Test Project"
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        task = Task(
            project_id=project.id,
            task_number=1,
            title="Timestamp Test Task"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    async def test_task_cascade_delete_with_project(self, db_session):
        """Task should be deleted when owning project is deleted (CASCADE)."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("task_cascade"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(
            user_id=user.id,
            title="Cascade Test Project"
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        task = Task(
            project_id=project.id,
            task_number=1,
            title="Cascade Test Task"
        )
        db_session.add(task)
        await db_session.commit()

        task_id = task.id

        # Delete the project
        await db_session.delete(project)
        await db_session.commit()

        # Task should be deleted due to CASCADE
        result = await db_session.execute(
            select(Task).where(Task.id == task_id)
        )
        assert result.scalar_one_or_none() is None

    async def test_task_project_relationship(self, db_session):
        """Task should have a relationship to Project."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("task_relationship"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(
            user_id=user.id,
            title="Relationship Test Project"
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        task = Task(
            project_id=project.id,
            task_number=1,
            title="Relationship Test Task"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Access the project through relationship
        assert task.project is not None
        assert task.project.id == project.id
        assert task.project.title == "Relationship Test Project"

    async def test_project_tasks_relationship(self, db_session):
        """Project should have a tasks relationship (backref)."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("multitask"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Multi-Task Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Create multiple tasks for this project
        task1 = Task(project_id=project.id, task_number=1, title="Task One")
        task2 = Task(project_id=project.id, task_number=2, title="Task Two")
        db_session.add_all([task1, task2])
        await db_session.commit()
        await db_session.refresh(project)

        # Access tasks through project relationship
        assert len(project.tasks) == 2
        task_titles = [t.title for t in project.tasks]
        assert "Task One" in task_titles
        assert "Task Two" in task_titles

    async def test_task_number_unique_per_project(self, db_session):
        """Task number should be unique within a project."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("unique_tasknum"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Unique TaskNum Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Create first task with task_number 1
        task1 = Task(
            project_id=project.id,
            task_number=1,
            title="First Task"
        )
        db_session.add(task1)
        await db_session.commit()

        # Try to create another task with the same task_number in the same project
        task2 = Task(
            project_id=project.id,
            task_number=1,  # Same number - should fail
            title="Second Task"
        )
        db_session.add(task2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_task_number_can_repeat_across_projects(self, db_session):
        """Same task number can be used in different projects."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("repeat_tasknum"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project1 = Project(user_id=user.id, title="Project One")
        project2 = Project(user_id=user.id, title="Project Two")
        db_session.add_all([project1, project2])
        await db_session.commit()
        await db_session.refresh(project1)
        await db_session.refresh(project2)

        # Create task with task_number 1 in both projects - should succeed
        task1 = Task(
            project_id=project1.id,
            task_number=1,
            title="Task in Project 1"
        )
        task2 = Task(
            project_id=project2.id,
            task_number=1,  # Same number, different project - should work
            title="Task in Project 2"
        )
        db_session.add_all([task1, task2])
        await db_session.commit()

        assert task1.task_number == 1
        assert task2.task_number == 1
        assert task1.project_id != task2.project_id

    async def test_task_upload_method_persistence(self, db_session):
        """Upload method should persist correctly."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("uploadmethod"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Upload Method Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        task = Task(
            project_id=project.id,
            task_number=1,
            title="Upload Test Task",
            upload_method="folder"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Retrieve and verify
        result = await db_session.execute(
            select(Task).where(Task.id == task.id)
        )
        retrieved = result.scalar_one()

        assert retrieved.upload_method == "folder"

    async def test_task_soft_delete_persistence(self, db_session):
        """Soft delete fields should persist correctly."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("task_softdelete"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Soft Delete Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        trashed_time = datetime.now(timezone.utc)
        scheduled_time = trashed_time + timedelta(days=30)

        task = Task(
            project_id=project.id,
            task_number=1,
            title="Soft Delete Test Task",
            deletion_status="trashed",
            trashed_at=trashed_time,
            scheduled_deletion_at=scheduled_time
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Retrieve and verify
        result = await db_session.execute(
            select(Task).where(Task.id == task.id)
        )
        retrieved = result.scalar_one()

        assert retrieved.deletion_status == "trashed"
        assert retrieved.trashed_at is not None
        assert retrieved.scheduled_deletion_at is not None

    async def test_task_sequential_numbering(self, db_session):
        """Tasks should have sequential numbering within a project."""
        from src.models.user import User
        from src.models.project import Project
        from src.models.task import Task

        user = User(
            email=unique_email("sequential"),
            password_hash="test_hash"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Sequential Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Create 3 tasks in sequence
        for i in range(1, 4):
            task = Task(
                project_id=project.id,
                task_number=i,
                title=f"Task {i}"
            )
            db_session.add(task)
        await db_session.commit()
        await db_session.refresh(project)

        # Verify sequential ordering
        task_numbers = sorted([t.task_number for t in project.tasks])
        assert task_numbers == [1, 2, 3]
