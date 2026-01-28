"""
Document API Endpoints - AI Code Learning Platform

This module provides REST API endpoints for learning document retrieval
and generation status checking.

Endpoints:
    GET /tasks/{task_id}/document - Get learning document
    GET /tasks/{task_id}/document/status - Get document generation status

Reference: api-spec.yaml §Document endpoints
Tasks: T097-T098 - Document API implementation
"""

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser
from src.api.exceptions import NotFoundError
from src.db.session import get_db
from src.services.document.document_generation_service import (
    get_document_generation_service,
)
from src.services.task_service import TaskService

# =============================================================================
# Pydantic Schemas
# =============================================================================


class LearningDocumentResponse(BaseModel):
    """
    Response schema for learning document content.

    Attributes:
        id: Document unique identifier
        task_id: Parent task ID
        generation_status: Status of generation
        content: 7-chapter structured content
        generated_at: When generation completed
    """

    id: UUID = Field(..., description="Document unique identifier")
    task_id: UUID = Field(..., description="Parent task ID")
    generation_status: str = Field(
        ..., description="Generation status (completed, in_progress, etc.)"
    )
    content: dict[str, Any] = Field(..., description="7-chapter structured content")
    generated_at: datetime | None = Field(None, description="When generation completed")

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    """
    Response schema for document generation status.

    Attributes:
        status: Generation status (pending, in_progress, completed, failed)
        task_id: Parent task ID
        document_id: Document ID (if exists)
        celery_task_id: Celery task ID for async tracking
        started_at: When generation started
        completed_at: When generation completed
        duration_seconds: Generation duration in seconds
        error: Error message if failed
        has_content: Whether document has content
    """

    status: str = Field(
        ...,
        description="Generation status: pending, in_progress, completed, failed, not_found",
    )
    task_id: str = Field(..., description="Parent task ID")
    document_id: str | None = Field(None, description="Document ID if exists")
    celery_task_id: str | None = Field(
        None, description="Celery task ID for async tracking"
    )
    started_at: str | None = Field(None, description="When generation started")
    completed_at: str | None = Field(None, description="When generation completed")
    duration_seconds: float | None = Field(
        None, description="Generation duration in seconds"
    )
    error: str | None = Field(None, description="Error message if failed")
    has_content: bool | None = Field(None, description="Whether document has content")


# =============================================================================
# Router
# =============================================================================

router = APIRouter()


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/tasks/{task_id}/document",
    response_model=LearningDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get learning document",
    description="Get 7-chapter learning document for task",
    responses={
        200: {"description": "Document retrieved successfully"},
        202: {"description": "Document is still generating"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not task owner)"},
        404: {"description": "Document not found"},
    },
)
async def get_document(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LearningDocumentResponse | JSONResponse:
    """
    Get learning document for a task.

    Returns the 7-chapter learning document if generation is completed.
    Returns 404 if document not found.
    Returns 202 if document is still generating (in_progress).

    Args:
        task_id: Task UUID
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        LearningDocumentResponse: Document content with all 7 chapters
        JSONResponse: 202 Accepted if document is still generating

    Raises:
        NotFoundError: If task doesn't exist or user doesn't own it
        NotFoundError: If document doesn't exist
    """
    # Verify task ownership
    task_service = TaskService(db)
    await task_service.get_by_id(task_id=task_id, user_id=current_user.id)

    # Get document
    doc_service = get_document_generation_service()
    document = await doc_service.get_document(task_id=task_id, session=db)

    if document is None:
        raise NotFoundError(
            detail=f"No learning document found for task '{task_id}'",
            resource="learning_document",
            resource_id=str(task_id),
        )

    # Return 202 if still generating
    if document.is_in_progress:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"message": "Document generation in progress"},
        )

    # Return 404 if not completed (pending or failed)
    if not document.is_completed:
        raise NotFoundError(
            detail=f"Document not available (status: {document.generation_status})",
            resource="learning_document",
            resource_id=str(task_id),
        )

    return LearningDocumentResponse(
        id=document.id,
        task_id=document.task_id,
        generation_status=document.generation_status,
        content=document.content,
        generated_at=document.generation_completed_at,
    )


@router.get(
    "/tasks/{task_id}/document/status",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document generation status",
    description="Check status of async document generation",
    responses={
        200: {"description": "Status retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access forbidden (not task owner)"},
    },
)
async def get_document_status(
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentStatusResponse:
    """
    Get document generation status for a task.

    Returns the current status of document generation including:
    - Status: pending, in_progress, completed, failed, not_found
    - Timestamps: started_at, completed_at
    - Error message if failed
    - Celery task ID for async tracking

    Args:
        task_id: Task UUID
        current_user: Authenticated user from dependency
        db: Database session

    Returns:
        DocumentStatusResponse: Generation status information

    Raises:
        NotFoundError: If task doesn't exist or user doesn't own it
    """
    # Verify task ownership
    task_service = TaskService(db)
    await task_service.get_by_id(task_id=task_id, user_id=current_user.id)

    # Get document status
    doc_service = get_document_generation_service()
    status_info = await doc_service.get_document_status(task_id=task_id, session=db)

    return DocumentStatusResponse(**status_info)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "router",
    "LearningDocumentResponse",
    "DocumentStatusResponse",
]
