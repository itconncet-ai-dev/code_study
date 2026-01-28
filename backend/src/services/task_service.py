"""
Task Service - AI Code Learning Platform

This module provides the TaskService for task management operations
including CRUD, soft delete, and auto-incrementing task numbers.

Features:
- Create new tasks with auto-incremented task_number
- Get task by ID with ownership validation
- List all tasks for a project
- Update task title and description
- Soft delete with 30-day trash retention
- Validate task ownership for authorization

Usage:
    from src.services.task_service import TaskService

    # In FastAPI endpoint with dependency injection
    async def create_task(
        project_id: UUID,
        request: CreateTaskRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        service = TaskService(db)
        task = await service.create(
            project_id=project_id,
            user_id=current_user.id,
            title=request.title,
            upload_method=request.upload_method
        )
        return task

Reference: data-model.md §Task entity
Task: T068 - Implement TaskService (create, get, update, soft delete)
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.models.task import Task
from src.services.project_service import ProjectService


# Trash retention period in days (per spec FR-009E)
TRASH_RETENTION_DAYS = 30

# Minimum title length
MIN_TITLE_LENGTH = 5


class TaskService:
    """
    Service class for task management operations.

    Provides methods for creating, retrieving, updating, and soft-deleting
    tasks. All operations are async and use SQLAlchemy AsyncSession.

    Attributes:
        db: AsyncSession for database operations

    Example:
        service = TaskService(db_session)
        task = await service.create(project_id, user_id, "My Task", "file")
        tasks = await service.get_project_tasks(project_id, user_id)
        updated = await service.update(task_id, user_id, title="New Title")
        await service.soft_delete(task_id, user_id)
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize TaskService with database session.

        Args:
            db: SQLAlchemy AsyncSession for database operations
        """
        self.db = db

    async def create(
        self,
        project_id: UUID,
        user_id: UUID,
        title: str,
        upload_method: str | None = None,
        description: str | None = None,
    ) -> Task:
        """
        Create a new task for a project.

        Creates a new task with an auto-incremented task_number within the project.
        The task_number is immutable once assigned.

        Args:
            project_id: UUID of the parent project
            user_id: UUID of the user (for ownership validation)
            title: Task title (required, minimum 5 characters)
            upload_method: How code was uploaded ('file', 'folder', 'paste')
            description: Optional task description (max 500 characters)

        Returns:
            Task: The newly created task instance

        Raises:
            ValidationError: If title is invalid or description too long
            ForbiddenError: If user doesn't own the project
            NotFoundError: If project doesn't exist

        Example:
            task = await service.create(
                project_id,
                user_id,
                "Calculator Code",
                "file",
                "Basic calculator implementation"
            )
        """
        # Validate title
        self._validate_title(title)

        # Validate description length
        if description and len(description) > 500:
            raise ValidationError(
                detail="Description cannot exceed 500 characters",
                field="description",
            )

        # Validate upload_method if provided
        if upload_method and upload_method not in ["file", "folder", "paste"]:
            raise ValidationError(
                detail="Upload method must be 'file', 'folder', or 'paste'",
                field="upload_method",
            )

        # Validate project ownership
        project_service = ProjectService(self.db)
        await project_service.validate_ownership(project_id, user_id)

        # Get next task number for this project
        task_number = await self._get_next_task_number(project_id)

        # Create new task
        task = Task(
            project_id=project_id,
            task_number=task_number,
            title=title,
            description=description,
            upload_method=upload_method,
            deletion_status="active",
        )

        # Persist to database
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def get_by_id(
        self,
        task_id: UUID,
        user_id: UUID,
        include_trashed: bool = False,
    ) -> Task:
        """
        Retrieve a task by its UUID with ownership validation.

        Args:
            task_id: The task's unique identifier
            user_id: The requesting user's UUID (for ownership check)
            include_trashed: If True, also return trashed tasks

        Returns:
            Task: The task instance if found and accessible

        Raises:
            NotFoundError: If task doesn't exist or is trashed (unless include_trashed)
            ForbiddenError: If user doesn't own the task's project

        Example:
            task = await service.get_by_id(task_id, current_user.id)

        Security Notes:
            - Always validates ownership via project
            - Returns NotFoundError for non-existent tasks (not Forbidden) to prevent enumeration
        """
        # Query task by ID with project relationship loaded
        stmt = select(Task).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()

        # Check if task exists
        if task is None:
            raise NotFoundError(
                detail=f"Task with ID '{task_id}' not found",
                resource="task",
                resource_id=str(task_id),
            )

        # Check project ownership
        project_service = ProjectService(self.db)
        await project_service.validate_ownership(task.project_id, user_id)

        # Check if trashed (unless include_trashed)
        if task.deletion_status == "trashed" and not include_trashed:
            raise NotFoundError(
                detail=f"Task with ID '{task_id}' not found",
                resource="task",
                resource_id=str(task_id),
            )

        return task

    async def get_project_tasks(
        self,
        project_id: UUID,
        user_id: UUID,
        include_trashed: bool = False,
    ) -> list[Task]:
        """
        Retrieve all tasks for a project in sequential order.

        Args:
            project_id: The project's UUID
            user_id: The user's UUID (for ownership validation)
            include_trashed: If True, include trashed tasks in results

        Returns:
            list[Task]: List of tasks ordered by task_number (may be empty)

        Raises:
            ForbiddenError: If user doesn't own the project
            NotFoundError: If project doesn't exist

        Example:
            tasks = await service.get_project_tasks(project_id, user_id)
        """
        # Validate project ownership
        project_service = ProjectService(self.db)
        await project_service.validate_ownership(project_id, user_id)

        # Build query with project_id filter
        stmt = select(Task).where(Task.project_id == project_id)

        # Filter by deletion status unless include_trashed
        if not include_trashed:
            stmt = stmt.where(Task.deletion_status == "active")

        # Order by task_number (sequential order)
        stmt = stmt.order_by(Task.task_number.asc())

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """
        Update a task's title and/or description.

        Args:
            task_id: The task's unique identifier
            user_id: The requesting user's UUID (for ownership check)
            title: New title (optional, if provided must be at least 5 characters)
            description: New description (optional, can be None to clear, max 500 chars)

        Returns:
            Task: The updated task instance

        Raises:
            NotFoundError: If task doesn't exist or is trashed
            ForbiddenError: If user doesn't own the task's project
            ValidationError: If title is invalid or description too long

        Example:
            updated = await service.update(task_id, user_id, title="New Title")
        """
        # Validate title if provided
        if title is not None:
            self._validate_title(title)

        # Validate description length if provided
        if description is not None and len(description) > 500:
            raise ValidationError(
                detail="Description cannot exceed 500 characters",
                field="description",
            )

        # Get the task (validates ownership and existence)
        task = await self.get_by_id(task_id, user_id)

        # Update fields if provided
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        # Update timestamp
        task.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def soft_delete(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Soft delete a task (move to trash).

        Sets the task's deletion_status to 'trashed', records trashed_at
        timestamp, and schedules permanent deletion after 30 days.

        Args:
            task_id: The task's unique identifier
            user_id: The requesting user's UUID (for ownership check)

        Raises:
            NotFoundError: If task doesn't exist or is already trashed
            ForbiddenError: If user doesn't own the task's project

        Example:
            await service.soft_delete(task_id, current_user.id)

        Business Rules:
            - Task is moved to trash (not permanently deleted)
            - Scheduled for permanent deletion after 30 days
            - User can restore from trash before scheduled deletion
        """
        # Get the task (validates ownership and existence)
        # Note: This will raise NotFoundError if already trashed
        task = await self.get_by_id(task_id, user_id)

        # Set soft delete fields
        now = datetime.now(timezone.utc)
        task.deletion_status = "trashed"
        task.trashed_at = now
        task.scheduled_deletion_at = now + timedelta(days=TRASH_RETENTION_DAYS)

        await self.db.commit()

    async def _get_next_task_number(self, project_id: UUID) -> int:
        """
        Get the next task number for a project.

        Task numbers start at 1 and are auto-incremented within each project.

        Args:
            project_id: The project's UUID

        Returns:
            int: The next task number (starting from 1)
        """
        # Get the maximum task_number for this project
        stmt = select(func.max(Task.task_number)).where(
            Task.project_id == project_id
        )
        result = await self.db.execute(stmt)
        max_number = result.scalar()

        # If no tasks exist, start at 1
        if max_number is None:
            return 1

        return max_number + 1

    def _validate_title(self, title: str | None) -> None:
        """
        Validate task title.

        Args:
            title: Title to validate

        Raises:
            ValidationError: If title is empty or less than 5 characters
        """
        if title is None or title.strip() == "":
            raise ValidationError(
                detail="Title is required and cannot be empty",
                field="title",
            )

        if len(title.strip()) < MIN_TITLE_LENGTH:
            raise ValidationError(
                detail=f"Title must be at least {MIN_TITLE_LENGTH} characters",
                field="title",
            )

    async def validate_ownership(
        self,
        task_id: UUID,
        user_id: UUID,
        include_trashed: bool = False,
    ) -> Task:
        """
        Validate that a user owns a task (via project ownership) and return the task.

        This method provides explicit ownership validation for use by other
        services that need to verify task access before performing operations.

        Args:
            task_id: The task's unique identifier
            user_id: The user's UUID to validate ownership against
            include_trashed: If True, also validate ownership of trashed tasks

        Returns:
            Task: The validated task instance

        Raises:
            NotFoundError: If task doesn't exist or is trashed (unless include_trashed)
            ForbiddenError: If user doesn't own the task's project

        Example:
            # In CodeAnalysisService before analyzing code
            task_service = TaskService(db)
            task = await task_service.validate_ownership(task_id, user_id)
            # Now safe to analyze code for this task

        Security Notes:
            - Always use this method before modifying task-related resources
            - Ownership is validated via project ownership
        """
        return await self.get_by_id(task_id, user_id, include_trashed)


__all__ = ["TaskService", "TRASH_RETENTION_DAYS", "MIN_TITLE_LENGTH"]
