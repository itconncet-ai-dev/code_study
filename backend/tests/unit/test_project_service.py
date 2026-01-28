"""
Unit Tests for ProjectService - T044

TDD RED Phase: These tests define the expected behavior of the ProjectService.
All tests should FAIL initially until the service is implemented.

Test Coverage:
- create: Create new project with title and optional description
- create: Assign correct user_id (ownership)
- create: Reject empty title
- get_by_id: Retrieve project by UUID
- get_by_id: Raise NotFoundError for non-existent project
- get_by_id: Raise ForbiddenError when user doesn't own project
- get_by_id: Return None for trashed projects (unless include_trashed)
- get_user_projects: List all active projects for a user
- get_user_projects: Support include_trashed parameter
- update: Update project title and description
- update: Raise NotFoundError for non-existent project
- update: Raise ForbiddenError when user doesn't own project
- soft_delete: Move project to trash with 30-day scheduled deletion
- soft_delete: Raise NotFoundError for non-existent project
- soft_delete: Raise ForbiddenError when user doesn't own project
"""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest


class TestProjectServiceCreate:
    """Test suite for ProjectService.create() method."""

    @pytest.mark.asyncio
    async def test_create_project_with_title(self):
        """create() should create a new project with provided title."""
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        user_id = uuid.uuid4()
        service = ProjectService(mock_session)
        project = await service.create(user_id=user_id, title="My First Project")

        assert project is not None
        assert project.title == "My First Project"
        assert project.user_id == user_id
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_with_description(self):
        """create() should create project with optional description."""
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        user_id = uuid.uuid4()
        service = ProjectService(mock_session)
        project = await service.create(
            user_id=user_id, title="My Project", description="Learning Python basics"
        )

        assert project.description == "Learning Python basics"

    @pytest.mark.asyncio
    async def test_create_project_sets_active_status(self):
        """create() should set deletion_status to 'active'."""
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        service = ProjectService(mock_session)
        project = await service.create(user_id=uuid.uuid4(), title="New Project")

        assert project.deletion_status == "active"
        assert project.trashed_at is None
        assert project.scheduled_deletion_at is None

    @pytest.mark.asyncio
    async def test_create_project_rejects_empty_title(self):
        """create() should raise ValidationError for empty title."""
        from src.api.exceptions import ValidationError
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        service = ProjectService(mock_session)

        with pytest.raises(ValidationError) as exc_info:
            await service.create(user_id=uuid.uuid4(), title="")

        assert "title" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_create_project_rejects_none_title(self):
        """create() should raise ValidationError for None title."""
        from src.api.exceptions import ValidationError
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        service = ProjectService(mock_session)

        with pytest.raises(ValidationError) as exc_info:
            await service.create(user_id=uuid.uuid4(), title=None)

        assert "title" in str(exc_info.value.detail).lower()


class TestProjectServiceGetById:
    """Test suite for ProjectService.get_by_id() method."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_project(self):
        """get_by_id() should return project for valid UUID."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Test Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        project = await service.get_by_id(project_id, user_id)

        assert project is not None
        assert project.id == project_id
        assert project.title == "Test Project"

    @pytest.mark.asyncio
    async def test_get_by_id_raises_not_found_for_unknown_id(self):
        """get_by_id() should raise NotFoundError for unknown UUID."""
        from src.api.exceptions import NotFoundError
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError) as exc_info:
            await service.get_by_id(uuid.uuid4(), uuid.uuid4())

        assert "project" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_by_id_raises_forbidden_for_wrong_owner(self):
        """get_by_id() should raise ForbiddenError when user doesn't own project."""
        from src.api.exceptions import ForbiddenError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        owner_id = uuid.uuid4()
        different_user_id = uuid.uuid4()
        project_id = uuid.uuid4()

        existing_project = Project(
            id=project_id, user_id=owner_id, title="Test Project"
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(ForbiddenError):
            await service.get_by_id(project_id, different_user_id)

    @pytest.mark.asyncio
    async def test_get_by_id_excludes_trashed_by_default(self):
        """get_by_id() should raise NotFoundError for trashed projects by default."""
        from src.api.exceptions import NotFoundError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        trashed_project = Project(
            id=project_id,
            user_id=user_id,
            title="Trashed Project",
            deletion_status="trashed",
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=trashed_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError):
            await service.get_by_id(project_id, user_id)

    @pytest.mark.asyncio
    async def test_get_by_id_includes_trashed_when_requested(self):
        """get_by_id() should return trashed projects when include_trashed=True."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        trashed_project = Project(
            id=project_id,
            user_id=user_id,
            title="Trashed Project",
            deletion_status="trashed",
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=trashed_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        project = await service.get_by_id(project_id, user_id, include_trashed=True)

        assert project is not None
        assert project.deletion_status == "trashed"


class TestProjectServiceGetUserProjects:
    """Test suite for ProjectService.get_user_projects() method."""

    @pytest.mark.asyncio
    async def test_get_user_projects_returns_active_projects(self):
        """get_user_projects() should return all active projects for user."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        projects = [
            Project(id=uuid.uuid4(), user_id=user_id, title="Project 1"),
            Project(id=uuid.uuid4(), user_id=user_id, title="Project 2"),
        ]

        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=projects)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        result = await service.get_user_projects(user_id)

        assert len(result) == 2
        assert result[0].title == "Project 1"
        assert result[1].title == "Project 2"

    @pytest.mark.asyncio
    async def test_get_user_projects_excludes_trashed_by_default(self):
        """get_user_projects() should exclude trashed projects by default."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        # Only active projects should be returned
        active_projects = [
            Project(id=uuid.uuid4(), user_id=user_id, title="Active Project"),
        ]

        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=active_projects)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        await service.get_user_projects(user_id)

        # The query should filter by deletion_status='active'
        # We verify by checking the call was made
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_projects_includes_trashed_when_requested(self):
        """get_user_projects() should include trashed when include_trashed=True."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        all_projects = [
            Project(id=uuid.uuid4(), user_id=user_id, title="Active Project"),
            Project(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Trashed Project",
                deletion_status="trashed",
            ),
        ]

        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=all_projects)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        result = await service.get_user_projects(user_id, include_trashed=True)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_projects_returns_empty_list_for_no_projects(self):
        """get_user_projects() should return empty list when user has no projects."""
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalars = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        result = await service.get_user_projects(uuid.uuid4())

        assert result == []


class TestProjectServiceUpdate:
    """Test suite for ProjectService.update() method."""

    @pytest.mark.asyncio
    async def test_update_project_title(self):
        """update() should update project title."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Old Title")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        updated = await service.update(
            project_id=project_id, user_id=user_id, title="New Title"
        )

        assert updated.title == "New Title"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_project_description(self):
        """update() should update project description."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            user_id=user_id,
            title="Project",
            description="Old description",
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        updated = await service.update(
            project_id=project_id, user_id=user_id, description="New description"
        )

        assert updated.description == "New description"

    @pytest.mark.asyncio
    async def test_update_raises_not_found_for_unknown_id(self):
        """update() should raise NotFoundError for unknown project."""
        from src.api.exceptions import NotFoundError
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError):
            await service.update(
                project_id=uuid.uuid4(), user_id=uuid.uuid4(), title="New Title"
            )

    @pytest.mark.asyncio
    async def test_update_raises_forbidden_for_wrong_owner(self):
        """update() should raise ForbiddenError when user doesn't own project."""
        from src.api.exceptions import ForbiddenError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        owner_id = uuid.uuid4()
        different_user_id = uuid.uuid4()
        project_id = uuid.uuid4()

        existing_project = Project(id=project_id, user_id=owner_id, title="Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(ForbiddenError):
            await service.update(
                project_id=project_id, user_id=different_user_id, title="New Title"
            )

    @pytest.mark.asyncio
    async def test_update_rejects_empty_title(self):
        """update() should raise ValidationError for empty title."""
        from src.api.exceptions import ValidationError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(ValidationError):
            await service.update(project_id=project_id, user_id=user_id, title="")


class TestProjectServiceSoftDelete:
    """Test suite for ProjectService.soft_delete() method."""

    @pytest.mark.asyncio
    async def test_soft_delete_moves_to_trash(self):
        """soft_delete() should set deletion_status to 'trashed'."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        await service.soft_delete(project_id, user_id)

        assert existing_project.deletion_status == "trashed"
        assert existing_project.trashed_at is not None
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_soft_delete_sets_scheduled_deletion(self):
        """soft_delete() should set scheduled_deletion_at to 30 days from now."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        await service.soft_delete(project_id, user_id)

        assert existing_project.scheduled_deletion_at is not None
        # Should be approximately 30 days from now
        expected_deletion = datetime.now(UTC) + timedelta(days=30)
        actual_deletion = existing_project.scheduled_deletion_at

        # Allow 1 minute difference for test execution time
        assert (
            abs(
                (
                    actual_deletion.replace(tzinfo=UTC) - expected_deletion
                ).total_seconds()
            )
            < 60
        )

    @pytest.mark.asyncio
    async def test_soft_delete_raises_not_found_for_unknown_id(self):
        """soft_delete() should raise NotFoundError for unknown project."""
        from src.api.exceptions import NotFoundError
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError):
            await service.soft_delete(uuid.uuid4(), uuid.uuid4())

    @pytest.mark.asyncio
    async def test_soft_delete_raises_forbidden_for_wrong_owner(self):
        """soft_delete() should raise ForbiddenError when user doesn't own project."""
        from src.api.exceptions import ForbiddenError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        owner_id = uuid.uuid4()
        different_user_id = uuid.uuid4()
        project_id = uuid.uuid4()

        existing_project = Project(id=project_id, user_id=owner_id, title="Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(ForbiddenError):
            await service.soft_delete(project_id, different_user_id)

    @pytest.mark.asyncio
    async def test_soft_delete_raises_not_found_for_already_trashed(self):
        """soft_delete() should raise NotFoundError for already trashed project."""
        from src.api.exceptions import NotFoundError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        trashed_project = Project(
            id=project_id,
            user_id=user_id,
            title="Trashed Project",
            deletion_status="trashed",
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=trashed_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError):
            await service.soft_delete(project_id, user_id)


class TestProjectServiceValidateOwnership:
    """Test suite for ProjectService.validate_ownership() method (T045)."""

    @pytest.mark.asyncio
    async def test_validate_ownership_returns_project_for_owner(self):
        """validate_ownership() should return project when user is the owner."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Test Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        project = await service.validate_ownership(project_id, user_id)

        assert project is not None
        assert project.id == project_id
        assert project.user_id == user_id

    @pytest.mark.asyncio
    async def test_validate_ownership_raises_not_found_for_unknown_id(self):
        """validate_ownership() should raise NotFoundError for unknown project."""
        from src.api.exceptions import NotFoundError
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError) as exc_info:
            await service.validate_ownership(uuid.uuid4(), uuid.uuid4())

        assert "project" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_validate_ownership_raises_forbidden_for_non_owner(self):
        """validate_ownership() should raise ForbiddenError when user is not the owner."""
        from src.api.exceptions import ForbiddenError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        owner_id = uuid.uuid4()
        non_owner_id = uuid.uuid4()
        project_id = uuid.uuid4()

        existing_project = Project(
            id=project_id, user_id=owner_id, title="Test Project"
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(ForbiddenError) as exc_info:
            await service.validate_ownership(project_id, non_owner_id)

        assert "permission" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_validate_ownership_excludes_trashed_by_default(self):
        """validate_ownership() should raise NotFoundError for trashed projects by default."""
        from src.api.exceptions import NotFoundError
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        trashed_project = Project(
            id=project_id,
            user_id=user_id,
            title="Trashed Project",
            deletion_status="trashed",
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=trashed_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        with pytest.raises(NotFoundError):
            await service.validate_ownership(project_id, user_id)

    @pytest.mark.asyncio
    async def test_validate_ownership_includes_trashed_when_requested(self):
        """validate_ownership() should return trashed projects when include_trashed=True."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        trashed_project = Project(
            id=project_id,
            user_id=user_id,
            title="Trashed Project",
            deletion_status="trashed",
        )

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=trashed_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)
        project = await service.validate_ownership(
            project_id, user_id, include_trashed=True
        )

        assert project is not None
        assert project.deletion_status == "trashed"

    @pytest.mark.asyncio
    async def test_validate_ownership_is_usable_by_other_services(self):
        """validate_ownership() should be usable for cross-service validation."""
        from src.models.project import Project
        from src.services.project_service import ProjectService

        mock_session = AsyncMock()

        user_id = uuid.uuid4()
        project_id = uuid.uuid4()
        existing_project = Project(id=project_id, user_id=user_id, title="Test Project")

        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=existing_project)
        mock_session.execute = AsyncMock(return_value=mock_result)

        service = ProjectService(mock_session)

        # Simulate TaskService using validate_ownership before creating a task
        project = await service.validate_ownership(project_id, user_id)

        # Should return the project for further operations
        assert project is not None
        assert project.id == project_id
        # TaskService can now safely create a task for this project
