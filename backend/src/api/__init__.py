"""
API Package - REST API endpoints for the Code Learning Platform.

This module provides the main API router structure with versioned endpoints.
All API endpoints are prefixed with /api/v1.

Router Structure:
    /api/v1/auth/*       - Authentication (register, login, logout, refresh)
    /api/v1/projects/*   - Project CRUD operations
    /api/v1/tasks/*      - Task management and code upload
    /api/v1/documents/*  - Learning document retrieval (via /tasks/{id}/document)
    /api/v1/practice/*   - Practice problems (via /tasks/{id}/practice)
    /api/v1/qa/*         - Question and answer (via /tasks/{id}/questions)
    /api/v1/progress/*   - Progress tracking (via /tasks/{id}/progress)
    /api/v1/trash/*      - Soft-deleted items management

Usage:
    from .api import api_router
    app.include_router(api_router, prefix="/api/v1")
"""

from fastapi import APIRouter

# Main API router - will be mounted at /api/v1
api_router = APIRouter()


def include_routers() -> None:
    """
    Include all sub-routers into the main API router.

    This function is called after all router modules are imported to avoid
    circular import issues. Each router is mounted with its appropriate prefix.

    Router modules should define a `router` variable of type APIRouter.
    """
    # Import and include routers as they are implemented
    # Each import is wrapped in try/except to allow partial implementation

    # Authentication routes
    try:
        from .auth import router as auth_router

        api_router.include_router(
            auth_router,
            prefix="/auth",
            tags=["Authentication"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Project routes
    try:
        from .projects import router as projects_router

        api_router.include_router(
            projects_router,
            prefix="/projects",
            tags=["Projects"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Task routes - project-level operations: /projects/{id}/tasks
    try:
        from .tasks import project_tasks_router

        api_router.include_router(
            project_tasks_router,
            prefix="/projects",  # Tasks are nested under projects: /projects/{id}/tasks
            tags=["Tasks"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Task routes - task-level operations: /tasks/{id}
    try:
        from .tasks import tasks_router

        api_router.include_router(
            tasks_router,
            prefix="/tasks",  # Individual task operations: /tasks/{id}
            tags=["Tasks"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Document routes (nested under tasks)
    try:
        from .documents import router as documents_router

        api_router.include_router(
            documents_router,
            prefix="",  # Documents are nested under tasks: /tasks/{id}/document
            tags=["Documents"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Practice routes (nested under tasks)
    try:
        from .practice import router as practice_router

        api_router.include_router(
            practice_router,
            prefix="",  # Practice is nested under tasks: /tasks/{id}/practice
            tags=["Practice"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Q&A routes (nested under tasks)
    try:
        from .qa import router as qa_router

        api_router.include_router(
            qa_router,
            prefix="",  # Q&A is nested under tasks: /tasks/{id}/questions
            tags=["Q&A"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Progress routes (nested under tasks)
    try:
        from .progress import router as progress_router

        api_router.include_router(
            progress_router,
            prefix="",  # Progress is nested under tasks: /tasks/{id}/progress
            tags=["Progress"],
        )
    except ImportError:
        pass  # Router not yet implemented

    # Trash routes
    try:
        from .trash import router as trash_router

        api_router.include_router(
            trash_router,
            prefix="/trash",
            tags=["Trash"],
        )
    except ImportError:
        pass  # Router not yet implemented


# Include all available routers
include_routers()


# Export the main router
__all__ = ["api_router"]
