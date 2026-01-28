"""
Task API Endpoints - AI Code Learning Platform

This module provides REST API endpoints for task management and code upload.

Endpoints:
    GET /projects/{project_id}/tasks - List project tasks
    POST /projects/{project_id}/tasks - Create task with code upload
    GET /tasks/{task_id} - Get task details
    PATCH /tasks/{task_id} - Update task
    DELETE /tasks/{task_id} - Soft delete task
    GET /tasks/{task_id}/code - Get uploaded code

Reference: api-spec.yaml §Task endpoints
Tasks: T070-T075 - Task API implementation
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

import logging

from src.api.dependencies import CurrentUser
from src.api.exceptions import ValidationError
from src.db.session import get_db
from src.services.code_analysis.code_upload_service import CodeUploadService
from src.services.task_service import TaskService

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Schemas
# =============================================================================


class CreateTaskRequest(BaseModel):
    """
    Request schema for creating a new task (for JSON body).

    Note: For multipart/form-data, use Form parameters in endpoint.

    Attributes:
        title: Task title (required, min 5 characters)
        upload_method: How code is uploaded ('file', 'folder', 'paste')
        code_text: Code text for paste method
        language: Language hint for paste method
    """

    title: str = Field(
        ...,
        min_length=5,
        description="Task title (required, minimum 5 characters)",
        examples=["Calculator Implementation"],
    )
    upload_method: str = Field(
        ...,
        description="Upload method: 'file', 'folder', or 'paste'",
        examples=["file"],
    )
    code_text: str | None = Field(
        default=None,
        description="Code text (required for paste method)",
        examples=["print('Hello, World!')"],
    )
    language: str | None = Field(
        default=None,
        description="Language hint for paste method (e.g., 'python', 'javascript')",
        examples=["python"],
    )


class UpdateTaskRequest(BaseModel):
    """
    Request schema for updating a task.

    Attributes:
        title: New task title (optional, min 5 characters)
        description: New task description (optional, max 500 characters)
    """

    title: str | None = Field(
        default=None,
        min_length=5,
        description="New task title (optional, minimum 5 characters)",
        examples=["Updated Task Title"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="New task description (optional, max 500 characters)",
        examples=["Updated description"],
    )


class CodeFileResponse(BaseModel):
    """
    Response schema for code file data.

    Attributes:
        id: File unique identifier
        file_name: Original filename
        file_path: Relative path (for folder uploads)
        file_extension: File extension
        file_size_bytes: File size in bytes
        mime_type: MIME type
    """

    id: UUID = Field(..., description="File unique identifier")
    file_name: str = Field(..., description="Original filename")
    file_path: str | None = Field(None, description="Relative path")
    file_extension: str | None = Field(None, description="File extension")
    file_size_bytes: int | None = Field(None, description="File size in bytes")
    mime_type: str | None = Field(None, description="MIME type")

    model_config = {"from_attributes": True}


class UploadedCodeResponse(BaseModel):
    """
    Response schema for uploaded code data.

    Attributes:
        id: UploadedCode unique identifier
        task_id: Parent task ID
        detected_language: Detected programming language
        complexity_level: Complexity level (beginner/intermediate/advanced)
        total_lines: Total lines of code
        total_files: Number of files
        upload_size_bytes: Total size in bytes
        created_at: Upload timestamp
        code_files: List of code files
    """

    id: UUID = Field(..., description="UploadedCode unique identifier")
    task_id: UUID = Field(..., description="Parent task ID")
    detected_language: str | None = Field(None, description="Detected language")
    complexity_level: str | None = Field(None, description="Complexity level")
    total_lines: int | None = Field(None, description="Total lines of code")
    total_files: int | None = Field(None, description="Number of files")
    upload_size_bytes: int | None = Field(None, description="Total size in bytes")
    created_at: datetime = Field(..., description="Upload timestamp")
    code_files: list[CodeFileResponse] = Field(
        default_factory=list, description="List of code files"
    )

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    """
    Response schema for task data.

    Attributes:
        id: Task unique identifier
        project_id: Parent project ID
        task_number: Sequential task number
        title: Task title
        description: Task description
        upload_method: Upload method used
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        deletion_status: 'active' or 'trashed'
        has_code: Whether code has been uploaded
    """

    id: UUID = Field(..., description="Task unique identifier")
    project_id: UUID = Field(..., description="Parent project ID")
    task_number: int = Field(..., description="Sequential task number")
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Task description")
    upload_method: str | None = Field(None, description="Upload method")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deletion_status: str = Field(..., description="Deletion status")
    has_code: bool = Field(default=False, description="Whether code uploaded")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "project_id": "650e8400-e29b-41d4-a716-446655440000",
                    "task_number": 1,
                    "title": "Calculator Implementation",
                    "description": "Basic calculator with operations",
                    "upload_method": "file",
                    "created_at": "2025-01-20T10:30:00Z",
                    "updated_at": "2025-01-20T15:45:00Z",
                    "deletion_status": "active",
                    "has_code": True,
                }
            ]
        },
    }


class TaskDetailResponse(BaseModel):
    """
    Response schema for task detail (includes uploaded code summary).

    Attributes:
        id: Task unique identifier
        project_id: Parent project ID
        task_number: Sequential task number
        title: Task title
        description: Task description
        upload_method: Upload method used
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        deletion_status: 'active' or 'trashed'
        uploaded_code_summary: Summary of uploaded code (if exists)
    """

    id: UUID = Field(..., description="Task unique identifier")
    project_id: UUID = Field(..., description="Parent project ID")
    task_number: int = Field(..., description="Sequential task number")
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Task description")
    upload_method: str | None = Field(None, description="Upload method")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deletion_status: str = Field(..., description="Deletion status")
    uploaded_code_summary: dict | None = Field(
        None, description="Summary of uploaded code"
    )

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """
    Response schema for task list endpoint.

    Attributes:
        tasks: List of tasks
        total: Total number of tasks
    """

    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")


# =============================================================================
# Helper Functions
# =============================================================================


def _task_to_response(task) -> TaskResponse:
    """
    Convert Task model to TaskResponse schema.

    Args:
        task: Task model instance

    Returns:
        TaskResponse: Serialized task data
    """
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        task_number=task.task_number,
        title=task.title,
        description=task.description,
        upload_method=task.upload_method,
        created_at=task.created_at,
        updated_at=task.updated_at,
        deletion_status=task.deletion_status,
        has_code=task.uploaded_code is not None,
    )


def _task_to_detail_response(task) -> TaskDetailResponse:
    """
    Convert Task model to TaskDetailResponse schema.

    Args:
        task: Task model instance

    Returns:
        TaskDetailResponse: Serialized task detail data
    """
    uploaded_code_summary = None
    if task.uploaded_code:
        uploaded_code_summary = {
            "detected_language": task.uploaded_code.detected_language,
            "complexity_level": task.uploaded_code.complexity_level,
            "total_lines": task.uploaded_code.total_lines,
            "total_files": task.uploaded_code.total_files,
            "upload_size_bytes": task.uploaded_code.upload_size_bytes,
        }

    return TaskDetailResponse(
        id=task.id,
        project_id=task.project_id,
        task_number=task.task_number,
        title=task.title,
        description=task.description,
        upload_method=task.upload_method,
        created_at=task.created_at,
        updated_at=task.updated_at,
        deletion_status=task.deletion_status,
        uploaded_code_summary=uploaded_code_summary,
    )


def _uploaded_code_to_response(uploaded_code) -> UploadedCodeResponse:
    """
    Convert UploadedCode model to UploadedCodeResponse schema.

    Args:
        uploaded_code: UploadedCode model instance

    Returns:
        UploadedCodeResponse: Serialized uploaded code data
    """
    code_files = [
        CodeFileResponse(
            id=cf.id,
            file_name=cf.file_name,
            file_path=cf.file_path,
            file_extension=cf.file_extension,
            file_size_bytes=cf.file_size_bytes,
            mime_type=cf.mime_type,
        )
        for cf in uploaded_code.code_files
    ]

    return UploadedCodeResponse(
        id=uploaded_code.id,
        task_id=uploaded_code.task_id,
        detected_language=uploaded_code.detected_language,
        complexity_level=uploaded_code.complexity_level,
        total_lines=uploaded_code.total_lines,
        total_files=uploaded_code.total_files,
        upload_size_bytes=uploaded_code.upload_size_bytes,
        created_at=uploaded_code.created_at,
        code_files=code_files,
    )


# =============================================================================
# Router Definitions
# =============================================================================

# Router for project-level task operations: /projects/{project_id}/tasks
project_tasks_router = APIRouter()

# Router for task-level operations: /tasks/{task_id}
tasks_router = APIRouter()

# Keep 'router' as alias for backward compatibility (points to project_tasks_router)
router = project_tasks_router


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/{project_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List project tasks",
    description="Get all tasks for a project in sequential order",
    responses={
        200: {"description": "Tasks retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not project owner)"},
        404: {"description": "Project not found"},
    },
)
async def get_project_tasks(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_trashed: bool = False,
) -> TaskListResponse:
    """
    Get all tasks for a project in sequential order.

    Returns tasks ordered by task_number. By default, only active tasks
    are returned. Set include_trashed=true to also include trashed tasks.

    Args:
        project_id: The project's UUID
        current_user: Authenticated user from dependency
        db: Database session
        include_trashed: Whether to include trashed tasks

    Returns:
        TaskListResponse: List of tasks with total count

    Raises:
        ForbiddenError: If user doesn't own the project
        NotFoundError: If project doesn't exist
    """
    task_service = TaskService(db)
    tasks = await task_service.get_project_tasks(
        project_id=project_id,
        user_id=current_user.id,
        include_trashed=include_trashed,
    )

    task_responses = [_task_to_response(t) for t in tasks]

    return TaskListResponse(
        tasks=task_responses,
        total=len(task_responses),
    )


@router.post(
    "/{project_id}/tasks",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task with code upload",
    description="Create a new task and upload code files",
    responses={
        201: {"description": "Task created successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not project owner)"},
        404: {"description": "Project not found"},
        413: {"description": "Upload exceeds 10MB limit"},
        422: {"description": "Validation error"},
    },
)
async def create_task(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    title: Annotated[str, Form(min_length=5, max_length=255)],
    upload_method: Annotated[str, Form()],
    files: list[UploadFile] | None = File(default=None),
    code_text: Annotated[str | None, Form()] = None,
    language: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form(max_length=500)] = None,
) -> TaskDetailResponse:
    """
    Create a new task with code upload.

    Accepts multipart/form-data with the following fields:
    - title (required): Task title (min 5 chars)
    - upload_method (required): 'file', 'folder', or 'paste'
    - files (optional): Array of files (for file/folder method)
    - code_text (optional): Code text (for paste method)
    - language (optional): Language hint (for paste method)
    - description (optional): Task description (max 500 chars)

    Args:
        project_id: The project's UUID
        current_user: Authenticated user from dependency
        db: Database session
        title: Task title
        upload_method: Upload method ('file', 'folder', 'paste')
        files: Uploaded files (for file/folder methods)
        code_text: Pasted code text (for paste method)
        language: Language hint (for paste method)
        description: Optional task description

    Returns:
        TaskDetailResponse: Created task with uploaded code summary

    Raises:
        ValidationError: If validation fails
        ForbiddenError: If user doesn't own the project
        NotFoundError: If project doesn't exist
    """
    # Validate upload_method
    if upload_method not in ["file", "folder", "paste"]:
        raise ValidationError(
            detail="Upload method must be 'file', 'folder', or 'paste'",
            field="upload_method",
        )

    # Create task
    task_service = TaskService(db)
    task = await task_service.create(
        project_id=project_id,
        user_id=current_user.id,
        title=title,
        upload_method=upload_method,
        description=description,
    )

    # Handle code upload based on method
    upload_service = CodeUploadService(db)

    if upload_method in ["file", "folder"]:
        # Validate files are provided
        if not files or len(files) == 0:
            raise ValidationError(
                detail="At least one file is required for file/folder upload",
                field="files",
            )

        # Read file contents
        file_data = []
        for file in files:
            content = await file.read()
            filename = file.filename or "unnamed"
            file_data.append((filename, content))

        # Handle based on method
        if upload_method == "file":
            await upload_service.handle_file_upload(
                task_id=task.id,
                user_id=current_user.id,
                files=file_data,
            )
        else:  # folder
            await upload_service.handle_folder_upload(
                task_id=task.id,
                user_id=current_user.id,
                files=file_data,
            )

    else:  # paste
        # Validate code_text is provided
        if not code_text:
            raise ValidationError(
                detail="code_text is required for paste upload method",
                field="code_text",
            )

        await upload_service.handle_paste_upload(
            task_id=task.id,
            user_id=current_user.id,
            code_text=code_text,
            language=language,
        )

    # Refresh task to get uploaded_code relationship
    await db.refresh(task)

    # T096: Auto-trigger document generation after code upload
    # Runs in background via Celery - does not block response
    if upload_method:
        try:
            from src.services.document.document_queue_service import (
                DocumentQueueService,
                AlreadyInQueueError,
            )
            queue_service = DocumentQueueService()
            celery_task_id = await queue_service.queue_generation(task.id, db)
            logger.info(
                f"Queued document generation for task {task.id} "
                f"(celery_task_id: {celery_task_id})"
            )
        except AlreadyInQueueError:
            logger.debug(f"Document generation already queued for task {task.id}")
        except Exception as e:
            # Log but don't fail task creation
            logger.warning(
                f"Failed to queue document generation for task {task.id}: {e}"
            )

    return _task_to_detail_response(task)


@tasks_router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task details",
    description="Get detailed information about a specific task",
    responses={
        200: {"description": "Task retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not task owner)"},
        404: {"description": "Task not found"},
    },
)
async def get_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskDetailResponse:
    """
    Get task details by ID.

    Requires task ownership (via project) - users can only access their own tasks.

    Args:
        task_id: Task UUID
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        TaskDetailResponse: Task data with uploaded code summary

    Raises:
        NotFoundError: If task doesn't exist or is trashed
        ForbiddenError: If user doesn't own the task's project
    """
    task_service = TaskService(db)
    task = await task_service.get_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )

    return _task_to_detail_response(task)


@tasks_router.patch(
    "/{task_id}",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description="Update task title and/or description",
    responses={
        200: {"description": "Task updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not task owner)"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskDetailResponse:
    """
    Update a task's title and/or description.

    At least one field must be provided. Empty request body is allowed
    but will result in no changes.

    Args:
        task_id: Task UUID
        request: Update data (title and/or description)
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        TaskDetailResponse: Updated task data

    Raises:
        NotFoundError: If task doesn't exist or is trashed
        ForbiddenError: If user doesn't own the task's project
        ValidationError: If validation fails
    """
    task_service = TaskService(db)
    task = await task_service.update(
        task_id=task_id,
        user_id=current_user.id,
        title=request.title,
        description=request.description,
    )

    return _task_to_detail_response(task)


@tasks_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Soft delete task (move to trash with 30-day retention)",
    responses={
        204: {"description": "Task deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not task owner)"},
        404: {"description": "Task not found"},
    },
)
async def delete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Soft delete a task.

    Moves the task to trash with 30-day retention period.
    After 30 days, the task will be permanently deleted.

    Args:
        task_id: Task UUID
        current_user: Authenticated user from dependency
        db: Database session

    Raises:
        NotFoundError: If task doesn't exist or is already trashed
        ForbiddenError: If user doesn't own the task's project
    """
    task_service = TaskService(db)
    await task_service.soft_delete(
        task_id=task_id,
        user_id=current_user.id,
    )


@tasks_router.get(
    "/{task_id}/code",
    response_model=UploadedCodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get uploaded code",
    description="Get uploaded code with file details",
    responses={
        200: {"description": "Uploaded code retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not task owner)"},
        404: {"description": "Task or uploaded code not found"},
    },
)
async def get_task_code(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UploadedCodeResponse:
    """
    Get uploaded code for a task.

    Returns code metadata and file information. Does not include
    actual file content - use file download endpoint for that.

    Args:
        task_id: Task UUID
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        UploadedCodeResponse: Uploaded code data with file list

    Raises:
        NotFoundError: If task doesn't exist or has no uploaded code
        ForbiddenError: If user doesn't own the task's project
    """
    task_service = TaskService(db)
    task = await task_service.get_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )

    if task.uploaded_code is None:
        from src.api.exceptions import NotFoundError

        raise NotFoundError(
            detail=f"No uploaded code found for task '{task_id}'",
            resource="uploaded_code",
            resource_id=str(task_id),
        )

    return _uploaded_code_to_response(task.uploaded_code)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "router",
    "project_tasks_router",
    "tasks_router",
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "TaskResponse",
    "TaskDetailResponse",
    "TaskListResponse",
    "UploadedCodeResponse",
    "CodeFileResponse",
]
