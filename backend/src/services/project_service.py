"""
Project Service - AI Code Learning Platform

This module provides the ProjectService for project management operations
including CRUD, soft delete, and ownership validation functionality.

Features:
- Create new projects with title and optional description
- Get project by ID with ownership validation
- List all projects for a user (active or including trashed)
- Update project title and description
- Soft delete with 30-day trash retention
- Validate project ownership for cross-service authorization

Usage:
    from src.services.project_service import ProjectService

    # In FastAPI endpoint with dependency injection
    async def create_project(
        request: CreateProjectRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        service = ProjectService(db)
        project = await service.create(current_user.id, request.title, request.description)
        return project

    # In TaskService for cross-service ownership validation
    async def create_task(project_id, user_id, ...):
        project_service = ProjectService(db)
        project = await project_service.validate_ownership(project_id, user_id)
        # Proceed with task creation

Reference: data-model.md §Project entity
Task: T044 - Implement ProjectService (create, get, update, soft delete)
Task: T045 - Implement project ownership validation
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.models.project import Project

# Trash retention period in days (per spec FR-009E)
TRASH_RETENTION_DAYS = 30


class ProjectService:
    """
    Service class for project management operations.

    Provides methods for creating, retrieving, updating, and soft-deleting
    projects. All operations are async and use SQLAlchemy AsyncSession.

    Attributes:
        db: AsyncSession for database operations

    Example:
        service = ProjectService(db_session)
        project = await service.create(user_id, "My Project", "Description")
        projects = await service.get_user_projects(user_id)
        updated = await service.update(project_id, user_id, title="New Title")
        await service.soft_delete(project_id, user_id)
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize ProjectService with database session.

        Args:
            db: SQLAlchemy AsyncSession for database operations
        """
        self.db = db

    async def create(
        self,
        user_id: UUID,
        title: str,
        description: str | None = None,
    ) -> Project:
        """
        Create a new project for a user.

        Creates a new project with the given title and optional description.
        The project is assigned to the specified user and set to 'active' status.

        Args:
            user_id: UUID of the project owner
            title: Project title (required, minimum 1 character)
            description: Optional project description

        Returns:
            Project: The newly created project instance

        Raises:
            ValidationError: If title is empty or None

        Example:
            project = await service.create(user_id, "Calculator App", "Learning basic Python")
        """
        # Validate title
        self._validate_title(title)

        # Create new project
        project = Project(
            user_id=user_id,
            title=title,
            description=description,
            deletion_status="active",
        )

        # Persist to database
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)

        return project

    async def get_by_id(
        self,
        project_id: UUID,
        user_id: UUID,
        include_trashed: bool = False,
    ) -> Project:
        """
        Retrieve a project by its UUID with ownership validation.

        Args:
            project_id: The project's unique identifier
            user_id: The requesting user's UUID (for ownership check)
            include_trashed: If True, also return trashed projects

        Returns:
            Project: The project instance if found and accessible

        Raises:
            NotFoundError: If project doesn't exist or is trashed (unless include_trashed)
            ForbiddenError: If user doesn't own the project

        Example:
            project = await service.get_by_id(project_id, current_user.id)

        Security Notes:
            - Always validates ownership to prevent unauthorized access
            - Returns NotFoundError for non-existent projects (not Forbidden) to prevent enumeration
        """
        # Query project by ID
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()

        # Check if project exists
        if project is None:
            raise NotFoundError(
                detail=f"Project with ID '{project_id}' not found",
                resource="project",
                resource_id=str(project_id),
            )

        # Check ownership
        if project.user_id != user_id:
            raise ForbiddenError(
                detail="You do not have permission to access this project"
            )

        # Check if trashed (unless include_trashed)
        if project.deletion_status == "trashed" and not include_trashed:
            raise NotFoundError(
                detail=f"Project with ID '{project_id}' not found",
                resource="project",
                resource_id=str(project_id),
            )

        return project

    async def get_user_projects(
        self,
        user_id: UUID,
        include_trashed: bool = False,
    ) -> list[Project]:
        """
        Retrieve all projects for a user.

        Args:
            user_id: The user's UUID
            include_trashed: If True, include trashed projects in results

        Returns:
            list[Project]: List of projects (may be empty)

        Example:
            projects = await service.get_user_projects(user_id)
            all_projects = await service.get_user_projects(user_id, include_trashed=True)
        """
        # Build query with user_id filter
        stmt = select(Project).where(Project.user_id == user_id)

        # Filter by deletion status unless include_trashed
        if not include_trashed:
            stmt = stmt.where(Project.deletion_status == "active")

        # Order by last activity (most recent first)
        stmt = stmt.order_by(Project.last_activity_at.desc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        project_id: UUID,
        user_id: UUID,
        title: str | None = None,
        description: str | None = None,
    ) -> Project:
        """
        Update a project's title and/or description.

        Args:
            project_id: The project's unique identifier
            user_id: The requesting user's UUID (for ownership check)
            title: New title (optional, if provided must be non-empty)
            description: New description (optional, can be None to clear)

        Returns:
            Project: The updated project instance

        Raises:
            NotFoundError: If project doesn't exist or is trashed
            ForbiddenError: If user doesn't own the project
            ValidationError: If title is provided but empty

        Example:
            updated = await service.update(project_id, user_id, title="New Title")
        """
        # Validate title if provided
        if title is not None:
            self._validate_title(title)

        # Get the project (validates ownership and existence)
        project = await self.get_by_id(project_id, user_id)

        # Update fields if provided
        if title is not None:
            project.title = title

        if description is not None:
            project.description = description

        # Update timestamp
        project.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(project)

        return project

    async def soft_delete(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Soft delete a project (move to trash).

        Sets the project's deletion_status to 'trashed', records trashed_at
        timestamp, and schedules permanent deletion after 30 days.

        Args:
            project_id: The project's unique identifier
            user_id: The requesting user's UUID (for ownership check)

        Raises:
            NotFoundError: If project doesn't exist or is already trashed
            ForbiddenError: If user doesn't own the project

        Example:
            await service.soft_delete(project_id, current_user.id)

        Business Rules:
            - Project is moved to trash (not permanently deleted)
            - Scheduled for permanent deletion after 30 days
            - User can restore from trash before scheduled deletion
        """
        # Get the project (validates ownership and existence)
        # Note: This will raise NotFoundError if already trashed
        project = await self.get_by_id(project_id, user_id)

        # Set soft delete fields
        now = datetime.now(UTC)
        project.deletion_status = "trashed"
        project.trashed_at = now
        project.scheduled_deletion_at = now + timedelta(days=TRASH_RETENTION_DAYS)

        await self.db.commit()

    def _validate_title(self, title: str | None) -> None:
        """
        Validate project title.

        Args:
            title: Title to validate

        Raises:
            ValidationError: If title is empty or None
        """
        if title is None or title.strip() == "":
            raise ValidationError(
                detail="Title is required and cannot be empty",
                field="title",
            )

    async def validate_ownership(
        self,
        project_id: UUID,
        user_id: UUID,
        include_trashed: bool = False,
    ) -> Project:
        """
        Validate that a user owns a project and return the project.

        This method provides explicit ownership validation for use by other
        services (e.g., TaskService) that need to verify project access before
        performing operations. It ensures consistent authorization checks
        across the application.

        Args:
            project_id: The project's unique identifier
            user_id: The user's UUID to validate ownership against
            include_trashed: If True, also validate ownership of trashed projects

        Returns:
            Project: The validated project instance

        Raises:
            NotFoundError: If project doesn't exist or is trashed (unless include_trashed)
            ForbiddenError: If user doesn't own the project

        Example:
            # In TaskService before creating a task
            project_service = ProjectService(db)
            project = await project_service.validate_ownership(project_id, user_id)
            # Now safe to create task for this project

            # In API endpoint for project-related operations
            await project_service.validate_ownership(project_id, current_user.id)
            # User is authorized, proceed with operation

        Security Notes:
            - Always use this method before modifying project-related resources
            - Returns NotFoundError for non-existent projects (not Forbidden)
              to prevent resource enumeration attacks
            - Ownership check prevents unauthorized access to other users' data
        """
        return await self.get_by_id(project_id, user_id, include_trashed)
