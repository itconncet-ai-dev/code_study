"""
Unit Tests for Project SQLAlchemy Model - T043

TDD RED Phase: These tests define the expected behavior of the Project model.
All tests should FAIL initially until the model is implemented.

Test Coverage:
- UUID primary key generation
- user_id foreign key field
- title field (required, min 1 char)
- description field (optional)
- Timestamps (created_at, updated_at)
- last_activity_at field
- Soft delete fields (deletion_status, trashed_at, scheduled_deletion_at)
- User relationship (back_populates)

Reference: data-model.md §Project entity
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class TestProjectModel:
    """Test suite for Project SQLAlchemy model."""

    def test_project_model_exists(self):
        """Project model class should be importable from models package."""
        from src.models.project import Project

        assert Project is not None
        assert Project.__tablename__ == "projects"

    def test_project_has_uuid_primary_key(self):
        """Project should have a UUID primary key field."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="Test Project")

        assert project.id is not None
        assert isinstance(project.id, uuid.UUID)

    def test_project_user_id_required(self):
        """Project user_id field should be set."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="Test Project")

        assert project.user_id == user_id
        assert isinstance(project.user_id, uuid.UUID)

    def test_project_title_field(self):
        """Project should have a title field."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="My Learning Project")

        assert project.title == "My Learning Project"

    def test_project_description_optional(self):
        """Project description field should be optional (nullable)."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="Test Project")

        assert project.description is None

    def test_project_description_can_be_set(self):
        """Project description field should accept text."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(
            user_id=user_id,
            title="Test Project",
            description="This is a detailed project description.",
        )

        assert project.description == "This is a detailed project description."

    def test_project_soft_delete_default(self):
        """Project deletion_status should default to 'active'."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="Test Project")

        assert project.deletion_status == "active"

    def test_project_trashed_at_nullable(self):
        """Project trashed_at should be nullable by default."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="Test Project")

        assert project.trashed_at is None

    def test_project_scheduled_deletion_at_nullable(self):
        """Project scheduled_deletion_at should be nullable by default."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        project = Project(user_id=user_id, title="Test Project")

        assert project.scheduled_deletion_at is None

    def test_project_has_timestamp_fields(self):
        """Project should have created_at, updated_at, last_activity_at fields."""
        from src.models.project import Project

        columns = [col.name for col in Project.__table__.columns]

        assert "created_at" in columns
        assert "updated_at" in columns
        assert "last_activity_at" in columns

    def test_project_model_table_columns(self):
        """Project model should have all expected columns per data-model.md."""
        from src.models.project import Project

        expected_columns = {
            "id",
            "user_id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "last_activity_at",
            "deletion_status",
            "trashed_at",
            "scheduled_deletion_at",
        }

        actual_columns = {col.name for col in Project.__table__.columns}

        assert expected_columns == actual_columns, (
            f"Missing columns: {expected_columns - actual_columns}, "
            f"Extra columns: {actual_columns - expected_columns}"
        )

    def test_project_soft_delete_can_be_set(self):
        """Project soft delete fields can be set for trashed state."""
        from src.models.project import Project

        user_id = uuid.uuid4()
        trashed_time = datetime.now(UTC)
        scheduled_time = trashed_time + timedelta(days=30)

        project = Project(
            user_id=user_id,
            title="Test Project",
            deletion_status="trashed",
            trashed_at=trashed_time,
            scheduled_deletion_at=scheduled_time,
        )

        assert project.deletion_status == "trashed"
        assert project.trashed_at == trashed_time
        assert project.scheduled_deletion_at == scheduled_time


@pytest.mark.asyncio
class TestProjectModelDatabase:
    """Database integration tests for Project model."""

    async def test_project_create_and_retrieve(self, db_session):
        """Project should be creatable and retrievable from database."""
        from src.models.project import Project
        from src.models.user import User

        # Create a user first (foreign key requirement)
        user = User(
            email="projectowner@example.com", password_hash="$2b$12$test_hash_value"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create project for this user
        project = Project(
            user_id=user.id,
            title="Test Project",
            description="A test project description",
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Verify persisted
        assert project.id is not None

        # Retrieve from database
        result = await db_session.execute(
            select(Project).where(Project.id == project.id)
        )
        retrieved_project = result.scalar_one()

        assert retrieved_project.title == "Test Project"
        assert retrieved_project.description == "A test project description"
        assert retrieved_project.user_id == user.id
        assert retrieved_project.deletion_status == "active"

    async def test_project_user_id_foreign_key(self, db_session):
        """Project user_id should reference existing user."""
        from src.models.project import Project

        # Try to create project with non-existent user
        fake_user_id = uuid.uuid4()
        project = Project(user_id=fake_user_id, title="Orphan Project")
        db_session.add(project)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_project_title_not_null_constraint(self, db_session):
        """Project title should have NOT NULL constraint."""
        from src.models.project import Project
        from src.models.user import User

        user = User(email="notitle@example.com", password_hash="test_hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id)
        db_session.add(project)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_project_timestamps_auto_set(self, db_session):
        """created_at, updated_at, last_activity_at should be automatically set."""
        from src.models.project import Project
        from src.models.user import User

        user = User(email="timestamps@example.com", password_hash="test_hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Timestamp Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        assert project.created_at is not None
        assert project.updated_at is not None
        assert project.last_activity_at is not None
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)
        assert isinstance(project.last_activity_at, datetime)

    async def test_project_cascade_delete_with_user(self, db_session):
        """Project should be deleted when owning user is deleted (CASCADE)."""
        from src.models.project import Project
        from src.models.user import User

        user = User(email="cascade@example.com", password_hash="test_hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Cascade Test Project")
        db_session.add(project)
        await db_session.commit()

        project_id = project.id

        # Delete the user
        await db_session.delete(user)
        await db_session.commit()

        # Project should be deleted due to CASCADE
        result = await db_session.execute(
            select(Project).where(Project.id == project_id)
        )
        assert result.scalar_one_or_none() is None

    async def test_project_user_relationship(self, db_session):
        """Project should have a relationship to User."""
        from src.models.project import Project
        from src.models.user import User

        user = User(email="relationship@example.com", password_hash="test_hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        project = Project(user_id=user.id, title="Relationship Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Access the user through relationship
        assert project.user is not None
        assert project.user.id == user.id
        assert project.user.email == "relationship@example.com"

    async def test_user_projects_relationship(self, db_session):
        """User should have a projects relationship (backref)."""
        from src.models.project import Project
        from src.models.user import User

        user = User(email="multiproject@example.com", password_hash="test_hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create multiple projects for this user
        project1 = Project(user_id=user.id, title="Project 1")
        project2 = Project(user_id=user.id, title="Project 2")
        db_session.add_all([project1, project2])
        await db_session.commit()
        await db_session.refresh(user)

        # Access projects through user relationship
        assert len(user.projects) == 2
        project_titles = [p.title for p in user.projects]
        assert "Project 1" in project_titles
        assert "Project 2" in project_titles

    async def test_project_soft_delete_persistence(self, db_session):
        """Soft delete fields should persist correctly."""
        from src.models.project import Project
        from src.models.user import User

        user = User(email="softdelete@example.com", password_hash="test_hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        trashed_time = datetime.now(UTC)
        scheduled_time = trashed_time + timedelta(days=30)

        project = Project(
            user_id=user.id,
            title="Soft Delete Test",
            deletion_status="trashed",
            trashed_at=trashed_time,
            scheduled_deletion_at=scheduled_time,
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        # Retrieve and verify
        result = await db_session.execute(
            select(Project).where(Project.id == project.id)
        )
        retrieved = result.scalar_one()

        assert retrieved.deletion_status == "trashed"
        assert retrieved.trashed_at is not None
        assert retrieved.scheduled_deletion_at is not None
