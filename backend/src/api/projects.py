"""
Project API Endpoints - AI Code Learning Platform

This module provides REST API endpoints for project management including
CRUD operations and soft delete functionality.

Endpoints:
    GET /projects - List user's projects
    POST /projects - Create new project
    GET /projects/{project_id} - Get project details
    PATCH /projects/{project_id} - Update project
    DELETE /projects/{project_id} - Soft delete project

Reference: api-spec.yaml §Project endpoints
Tasks: T046-T050 - Project API implementation
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser
from src.db.session import get_db
from src.services.project_service import ProjectService

# =============================================================================
# Pydantic Schemas
# =============================================================================


class CreateProjectRequest(BaseModel):
    """
    Request schema for creating a new project.

    Attributes:
        title: Project title (1-255 characters, required)
        description: Optional project description
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Project title (required, 1-255 characters)",
        examples=["My Python Learning Project"],
    )
    description: str | None = Field(
        default=None,
        description="Optional project description",
        examples=["Learning Python fundamentals and data structures"],
    )


class UpdateProjectRequest(BaseModel):
    """
    Request schema for updating a project.

    Attributes:
        title: New project title (optional, 1-255 characters)
        description: New project description (optional)
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New project title (optional)",
        examples=["Updated Project Title"],
    )
    description: str | None = Field(
        default=None,
        description="New project description (optional)",
        examples=["Updated description"],
    )


class ProjectResponse(BaseModel):
    """
    Response schema for project data.

    Attributes:
        id: Project unique identifier
        title: Project title
        description: Project description
        created_at: Project creation timestamp
        last_activity_at: Last activity timestamp
        deletion_status: 'active' or 'trashed'
        trashed_at: When project was trashed (if applicable)
        task_count: Total number of tasks
        completed_task_count: Number of completed tasks
        progress_percentage: Overall progress (0-100)
    """

    id: UUID = Field(..., description="Project unique identifier")
    title: str = Field(..., description="Project title")
    description: str | None = Field(None, description="Project description")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_activity_at: datetime = Field(..., description="Last activity timestamp")
    deletion_status: str = Field(..., description="Deletion status")
    trashed_at: datetime | None = Field(None, description="Trash timestamp")
    task_count: int = Field(default=0, description="Total task count")
    completed_task_count: int = Field(default=0, description="Completed task count")
    progress_percentage: int = Field(default=0, description="Progress percentage")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "My Learning Project",
                    "description": "Learning Python basics",
                    "created_at": "2025-01-20T10:30:00Z",
                    "last_activity_at": "2025-01-20T15:45:00Z",
                    "deletion_status": "active",
                    "trashed_at": None,
                    "task_count": 5,
                    "completed_task_count": 2,
                    "progress_percentage": 40,
                }
            ]
        },
    }


class ProjectListResponse(BaseModel):
    """
    Response schema for project list endpoint.

    Attributes:
        projects: List of projects
        total: Total number of projects
    """

    projects: list[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "projects": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Project 1",
                            "description": "First project",
                            "created_at": "2025-01-20T10:30:00Z",
                            "last_activity_at": "2025-01-20T15:45:00Z",
                            "deletion_status": "active",
                            "trashed_at": None,
                            "task_count": 3,
                            "completed_task_count": 1,
                            "progress_percentage": 33,
                        }
                    ],
                    "total": 1,
                }
            ]
        },
    }


# =============================================================================
# Helper Functions
# =============================================================================


def _project_to_response(project) -> ProjectResponse:
    """
    Convert Project model to ProjectResponse schema.

    Args:
        project: Project model instance

    Returns:
        ProjectResponse: Serialized project data
    """
    # TODO: Calculate task counts and progress when Task model is implemented
    # For now, return default values
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        created_at=project.created_at,
        last_activity_at=project.last_activity_at,
        deletion_status=project.deletion_status,
        trashed_at=project.trashed_at,
        task_count=0,
        completed_task_count=0,
        progress_percentage=0,
    )


# =============================================================================
# Router Definition
# =============================================================================

router = APIRouter()


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user projects",
    description="Get all projects for the authenticated user",
    responses={
        200: {"description": "Projects retrieved successfully"},
        401: {"description": "Not authenticated"},
    },
)
async def get_projects(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_trashed: bool = False,
) -> ProjectListResponse:
    """
    Get all projects for the authenticated user.

    By default, only active projects are returned. Set include_trashed=true
    to also include trashed projects.

    Args:
        current_user: Authenticated user from dependency
        db: Database session
        include_trashed: Whether to include trashed projects

    Returns:
        ProjectListResponse: List of projects with total count
    """
    project_service = ProjectService(db)
    projects = await project_service.get_user_projects(
        user_id=current_user.id,
        include_trashed=include_trashed,
    )

    project_responses = [_project_to_response(p) for p in projects]

    return ProjectListResponse(
        projects=project_responses,
        total=len(project_responses),
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
    description="Create a new project for the authenticated user",
    responses={
        201: {"description": "Project created successfully"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"},
    },
)
async def create_project(
    request: CreateProjectRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectResponse:
    """
    Create a new project.

    Requires a title (1-255 characters). Description is optional.

    Args:
        request: Project creation data
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        ProjectResponse: Created project data

    Raises:
        ValidationError: If title is invalid
    """
    project_service = ProjectService(db)
    project = await project_service.create(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
    )

    return _project_to_response(project)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
    description="Get detailed information about a specific project",
    responses={
        200: {"description": "Project retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not project owner)"},
        404: {"description": "Project not found"},
    },
)
async def get_project(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectResponse:
    """
    Get project details by ID.

    Requires project ownership - users can only access their own projects.

    Args:
        project_id: Project UUID
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        ProjectResponse: Project data with task summary

    Raises:
        NotFoundError: If project doesn't exist or is trashed
        ForbiddenError: If user doesn't own the project
    """
    project_service = ProjectService(db)
    project = await project_service.get_by_id(
        project_id=project_id,
        user_id=current_user.id,
    )

    return _project_to_response(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project",
    description="Update project title and/or description",
    responses={
        200: {"description": "Project updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not project owner)"},
        404: {"description": "Project not found"},
        422: {"description": "Validation error"},
    },
)
async def update_project(
    project_id: UUID,
    request: UpdateProjectRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectResponse:
    """
    Update a project's title and/or description.

    At least one field must be provided. Empty request body is allowed
    but will result in no changes.

    Args:
        project_id: Project UUID
        request: Update data (title and/or description)
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        ProjectResponse: Updated project data

    Raises:
        NotFoundError: If project doesn't exist or is trashed
        ForbiddenError: If user doesn't own the project
        ValidationError: If title is provided but empty
    """
    project_service = ProjectService(db)
    project = await project_service.update(
        project_id=project_id,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
    )

    return _project_to_response(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Soft delete project (move to trash with 30-day retention)",
    responses={
        204: {"description": "Project deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not project owner)"},
        404: {"description": "Project not found"},
    },
)
async def delete_project(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Soft delete a project.

    Moves the project to trash with 30-day retention period.
    After 30 days, the project will be permanently deleted.

    Args:
        project_id: Project UUID
        current_user: Authenticated user from dependency
        db: Database session

    Raises:
        NotFoundError: If project doesn't exist or is already trashed
        ForbiddenError: If user doesn't own the project
    """
    project_service = ProjectService(db)
    await project_service.soft_delete(
        project_id=project_id,
        user_id=current_user.id,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "router",
    "CreateProjectRequest",
    "UpdateProjectRequest",
    "ProjectResponse",
    "ProjectListResponse",
]
