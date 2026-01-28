"""
API Exception Handling - Custom exceptions and error response schemas.

This module provides a comprehensive exception handling system for the
AI Code Learning Platform API.

Features:
- Custom exception classes for common HTTP errors
- Pydantic schemas for consistent error responses
- Exception handler functions for FastAPI integration
- Request context preservation in error responses

Usage:
    # Raising exceptions
    from backend.src.api.exceptions import NotFoundError, ValidationError

    raise NotFoundError(detail="Project not found", resource="project", resource_id="123")
    raise ValidationError(detail="Invalid email format", field="email")

    # Registering handlers in main.py
    from backend.src.api.exceptions import register_exception_handlers

    register_exception_handlers(app)
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


# =============================================================================
# Error Codes Enum
# =============================================================================


class ErrorCode(str, Enum):
    """
    Standard error codes for API responses.

    These codes allow clients to programmatically handle specific error types.
    """

    # Authentication errors (AUTH_xxx)
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_UNAUTHORIZED = "AUTH_UNAUTHORIZED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    AUTH_EMAIL_ALREADY_EXISTS = "AUTH_EMAIL_ALREADY_EXISTS"

    # Validation errors (VALIDATION_xxx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    VALIDATION_FIELD_REQUIRED = "VALIDATION_FIELD_REQUIRED"
    VALIDATION_FIELD_INVALID = "VALIDATION_FIELD_INVALID"

    # Resource errors (RESOURCE_xxx)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_DELETED = "RESOURCE_DELETED"

    # File upload errors (FILE_xxx)
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_TYPE_NOT_ALLOWED = "FILE_TYPE_NOT_ALLOWED"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_BINARY_NOT_ALLOWED = "FILE_BINARY_NOT_ALLOWED"

    # Rate limiting (RATE_xxx)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # External service errors (SERVICE_xxx)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    SERVICE_AI_ERROR = "SERVICE_AI_ERROR"
    SERVICE_TIMEOUT = "SERVICE_TIMEOUT"

    # Internal errors (INTERNAL_xxx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INTERNAL_DATABASE_ERROR = "INTERNAL_DATABASE_ERROR"


# =============================================================================
# Error Response Schemas
# =============================================================================


class ErrorDetail(BaseModel):
    """
    Detailed error information for a specific field or issue.
    """

    field: str | None = Field(
        default=None,
        description="The field name that caused the error (for validation errors)",
        examples=["email"],
    )
    message: str = Field(
        description="Human-readable error message",
        examples=["Email format is invalid"],
    )
    code: str | None = Field(
        default=None,
        description="Specific error code for this detail",
        examples=["VALIDATION_FIELD_INVALID"],
    )


class ErrorResponse(BaseModel):
    """
    Standard error response schema for all API errors.

    This schema ensures consistent error formatting across all endpoints.
    """

    success: bool = Field(
        default=False,
        description="Always false for error responses",
    )
    error: str = Field(
        description="Error code for programmatic handling",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        description="Human-readable error message",
        examples=["Validation failed for the provided data"],
    )
    details: list[ErrorDetail] | None = Field(
        default=None,
        description="Additional error details (e.g., field-specific validation errors)",
    )
    request_id: str | None = Field(
        default=None,
        description="Request ID for tracing and debugging",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the error occurred",
    )
    path: str | None = Field(
        default=None,
        description="Request path that caused the error",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": False,
                    "error": "RESOURCE_NOT_FOUND",
                    "message": "Project with ID '123' not found",
                    "details": None,
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2025-01-20T10:30:00Z",
                    "path": "/api/v1/projects/123",
                }
            ]
        }
    }


# =============================================================================
# Base Exception Class
# =============================================================================


class APIException(Exception):
    """
    Base exception class for all API exceptions.

    Attributes:
        status_code: HTTP status code
        error_code: Application-specific error code
        detail: Human-readable error message
        headers: Optional HTTP headers to include in response
    """

    status_code: int = 500
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR
    detail: str = "An unexpected error occurred"
    headers: dict[str, str] | None = None

    def __init__(
        self,
        detail: str | None = None,
        error_code: ErrorCode | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the exception.

        Args:
            detail: Human-readable error message
            error_code: Application-specific error code
            headers: Optional HTTP headers to include in response
            **kwargs: Additional context stored in self.context
        """
        self.detail = detail or self.detail
        self.error_code = error_code or self.error_code
        self.headers = headers or self.headers
        self.context = kwargs
        super().__init__(self.detail)


# =============================================================================
# Authentication Exceptions (4xx)
# =============================================================================


class UnauthorizedError(APIException):
    """
    Raised when authentication is required but not provided or invalid.
    HTTP 401 Unauthorized
    """

    status_code = 401
    error_code = ErrorCode.AUTH_UNAUTHORIZED
    detail = "Authentication required"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidCredentialsError(APIException):
    """
    Raised when login credentials are invalid.
    HTTP 401 Unauthorized
    """

    status_code = 401
    error_code = ErrorCode.AUTH_INVALID_CREDENTIALS
    detail = "Invalid email or password"


class TokenExpiredError(APIException):
    """
    Raised when an access or refresh token has expired.
    HTTP 401 Unauthorized
    """

    status_code = 401
    error_code = ErrorCode.AUTH_TOKEN_EXPIRED
    detail = "Token has expired"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenInvalidError(APIException):
    """
    Raised when a token is malformed or invalid.
    HTTP 401 Unauthorized
    """

    status_code = 401
    error_code = ErrorCode.AUTH_TOKEN_INVALID
    detail = "Token is invalid"
    headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenError(APIException):
    """
    Raised when user is authenticated but lacks permission.
    HTTP 403 Forbidden
    """

    status_code = 403
    error_code = ErrorCode.AUTH_FORBIDDEN
    detail = "You do not have permission to perform this action"


# =============================================================================
# Resource Exceptions (4xx)
# =============================================================================


class NotFoundError(APIException):
    """
    Raised when a requested resource does not exist.
    HTTP 404 Not Found
    """

    status_code = 404
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    detail = "Resource not found"

    def __init__(
        self,
        detail: str | None = None,
        resource: str | None = None,
        resource_id: str | UUID | int | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize NotFoundError with optional resource context.

        Args:
            detail: Custom error message
            resource: Type of resource (e.g., "project", "task", "user")
            resource_id: ID of the resource that wasn't found
        """
        if detail is None and resource and resource_id:
            detail = f"{resource.capitalize()} with ID '{resource_id}' not found"
        elif detail is None and resource:
            detail = f"{resource.capitalize()} not found"

        super().__init__(detail=detail, resource=resource, resource_id=resource_id, **kwargs)


class ConflictError(APIException):
    """
    Raised when there's a conflict with the current resource state.
    HTTP 409 Conflict
    """

    status_code = 409
    error_code = ErrorCode.RESOURCE_CONFLICT
    detail = "Resource conflict"


class AlreadyExistsError(APIException):
    """
    Raised when attempting to create a resource that already exists.
    HTTP 409 Conflict
    """

    status_code = 409
    error_code = ErrorCode.RESOURCE_ALREADY_EXISTS
    detail = "Resource already exists"

    def __init__(
        self,
        detail: str | None = None,
        resource: str | None = None,
        field: str | None = None,
        value: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize AlreadyExistsError with context.

        Args:
            detail: Custom error message
            resource: Type of resource
            field: Field that caused the conflict (e.g., "email")
            value: Value that already exists
        """
        if detail is None and resource and field:
            detail = f"{resource.capitalize()} with {field} already exists"

        super().__init__(
            detail=detail, resource=resource, field=field, value=value, **kwargs
        )


class ResourceDeletedError(APIException):
    """
    Raised when attempting to access a soft-deleted resource.
    HTTP 410 Gone
    """

    status_code = 410
    error_code = ErrorCode.RESOURCE_DELETED
    detail = "Resource has been deleted"


# =============================================================================
# Validation Exceptions (4xx)
# =============================================================================


class ValidationError(APIException):
    """
    Raised when request data fails validation.
    HTTP 422 Unprocessable Entity
    """

    status_code = 422
    error_code = ErrorCode.VALIDATION_ERROR
    detail = "Validation error"

    def __init__(
        self,
        detail: str | None = None,
        errors: list[ErrorDetail] | None = None,
        field: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize ValidationError with optional field-specific errors.

        Args:
            detail: General validation error message
            errors: List of field-specific error details
            field: Single field name (convenience for single-field errors)
        """
        self.errors = errors or []

        if field and not errors:
            self.errors = [
                ErrorDetail(
                    field=field,
                    message=detail or "Field validation failed",
                    code=ErrorCode.VALIDATION_FIELD_INVALID.value,
                )
            ]

        super().__init__(detail=detail, **kwargs)


# =============================================================================
# File Upload Exceptions (4xx)
# =============================================================================


class FileTooLargeError(APIException):
    """
    Raised when uploaded file exceeds size limit.
    HTTP 413 Payload Too Large
    """

    status_code = 413
    error_code = ErrorCode.FILE_TOO_LARGE
    detail = "File size exceeds the maximum allowed limit"

    def __init__(
        self,
        detail: str | None = None,
        max_size_mb: int = 10,
        actual_size_mb: float | None = None,
        **kwargs: Any,
    ) -> None:
        if detail is None:
            detail = f"File size exceeds the maximum limit of {max_size_mb}MB"
            if actual_size_mb is not None:
                detail += f" (received: {actual_size_mb:.2f}MB)"

        super().__init__(
            detail=detail, max_size_mb=max_size_mb, actual_size_mb=actual_size_mb, **kwargs
        )


class FileTypeNotAllowedError(APIException):
    """
    Raised when uploaded file type is not allowed.
    HTTP 415 Unsupported Media Type
    """

    status_code = 415
    error_code = ErrorCode.FILE_TYPE_NOT_ALLOWED
    detail = "File type is not allowed"

    def __init__(
        self,
        detail: str | None = None,
        file_type: str | None = None,
        allowed_types: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if detail is None and file_type:
            detail = f"File type '{file_type}' is not allowed"
            if allowed_types:
                detail += f". Allowed types: {', '.join(allowed_types)}"

        super().__init__(
            detail=detail, file_type=file_type, allowed_types=allowed_types, **kwargs
        )


class BinaryFileNotAllowedError(APIException):
    """
    Raised when a binary file is uploaded where text is expected.
    HTTP 415 Unsupported Media Type
    """

    status_code = 415
    error_code = ErrorCode.FILE_BINARY_NOT_ALLOWED
    detail = "Binary files are not allowed. Please upload text-based code files only"


# =============================================================================
# Rate Limiting Exceptions (4xx)
# =============================================================================


class RateLimitExceededError(APIException):
    """
    Raised when rate limit is exceeded.
    HTTP 429 Too Many Requests
    """

    status_code = 429
    error_code = ErrorCode.RATE_LIMIT_EXCEEDED
    detail = "Rate limit exceeded. Please try again later"

    def __init__(
        self,
        detail: str | None = None,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        super().__init__(detail=detail, headers=headers, retry_after=retry_after, **kwargs)


# =============================================================================
# External Service Exceptions (5xx)
# =============================================================================


class ServiceUnavailableError(APIException):
    """
    Raised when an external service is unavailable.
    HTTP 503 Service Unavailable
    """

    status_code = 503
    error_code = ErrorCode.SERVICE_UNAVAILABLE
    detail = "Service temporarily unavailable. Please try again later"


class AIServiceError(APIException):
    """
    Raised when AI service (Gemini API) fails.
    HTTP 503 Service Unavailable
    """

    status_code = 503
    error_code = ErrorCode.SERVICE_AI_ERROR
    detail = "AI service is temporarily unavailable. Please try again later"

    def __init__(
        self,
        detail: str | None = None,
        is_retrying: bool = False,
        retry_attempt: int | None = None,
        **kwargs: Any,
    ) -> None:
        if is_retrying and retry_attempt:
            detail = f"AI service error. Retrying... (attempt {retry_attempt})"

        super().__init__(
            detail=detail, is_retrying=is_retrying, retry_attempt=retry_attempt, **kwargs
        )


class ServiceTimeoutError(APIException):
    """
    Raised when an external service request times out.
    HTTP 504 Gateway Timeout
    """

    status_code = 504
    error_code = ErrorCode.SERVICE_TIMEOUT
    detail = "Request timed out. Please try again"


# =============================================================================
# Internal Exceptions (5xx)
# =============================================================================


class InternalError(APIException):
    """
    Raised for unexpected internal errors.
    HTTP 500 Internal Server Error
    """

    status_code = 500
    error_code = ErrorCode.INTERNAL_ERROR
    detail = "An unexpected error occurred"


class DatabaseError(APIException):
    """
    Raised for database-related errors.
    HTTP 500 Internal Server Error
    """

    status_code = 500
    error_code = ErrorCode.INTERNAL_DATABASE_ERROR
    detail = "A database error occurred"


# =============================================================================
# Exception Handlers
# =============================================================================


def _get_request_context(request: Request) -> dict[str, str | None]:
    """
    Extract context information from the request.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with request_id and path
    """
    request_id = getattr(request.state, "request_id", None)
    return {
        "request_id": request_id,
        "path": str(request.url.path),
    }


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handler for custom APIException and its subclasses.

    Args:
        request: FastAPI request object
        exc: The APIException instance

    Returns:
        JSONResponse with standardized error format
    """
    context = _get_request_context(request)

    # Build error details for validation errors
    details = None
    if isinstance(exc, ValidationError) and exc.errors:
        details = [error.model_dump() for error in exc.errors]

    response = ErrorResponse(
        error=exc.error_code.value,
        message=exc.detail,
        details=details,
        request_id=context["request_id"],
        path=context["path"],
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode="json"),
        headers=exc.headers,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unexpected exceptions.

    This catches any unhandled exceptions and returns a generic 500 error
    while logging the actual error for debugging.

    Args:
        request: FastAPI request object
        exc: The exception instance

    Returns:
        JSONResponse with generic error message
    """
    context = _get_request_context(request)

    # Log the actual error (import logging when needed)
    import logging
    logger = logging.getLogger(__name__)
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}",
        extra={"request_id": context["request_id"], "path": context["path"]},
        exc_info=True,
    )

    response = ErrorResponse(
        error=ErrorCode.INTERNAL_ERROR.value,
        message="An unexpected error occurred",
        request_id=context["request_id"],
        path=context["path"],
    )

    return JSONResponse(
        status_code=500,
        content=response.model_dump(mode="json"),
    )


async def validation_exception_handler(
    request: Request, exc: "RequestValidationError"
) -> JSONResponse:
    """
    Handler for Pydantic/FastAPI validation errors.

    Converts FastAPI's RequestValidationError into our standard error format.

    Args:
        request: FastAPI request object
        exc: FastAPI RequestValidationError

    Returns:
        JSONResponse with standardized validation error format
    """
    from fastapi.exceptions import RequestValidationError

    context = _get_request_context(request)

    # Convert Pydantic errors to our format
    details = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append(
            ErrorDetail(
                field=field_path or None,
                message=error["msg"],
                code=ErrorCode.VALIDATION_FIELD_INVALID.value,
            ).model_dump()
        )

    response = ErrorResponse(
        error=ErrorCode.VALIDATION_ERROR.value,
        message="Validation error",
        details=details,
        request_id=context["request_id"],
        path=context["path"],
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.

    This function should be called during application setup.

    Args:
        app: FastAPI application instance

    Usage:
        from backend.src.api.exceptions import register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)
    """
    from fastapi.exceptions import RequestValidationError

    # Register handler for our custom exceptions
    app.add_exception_handler(APIException, api_exception_handler)

    # Register handler for FastAPI validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Register handler for all other exceptions
    app.add_exception_handler(Exception, generic_exception_handler)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Error codes
    "ErrorCode",
    # Response schemas
    "ErrorDetail",
    "ErrorResponse",
    # Base exception
    "APIException",
    # Authentication exceptions
    "UnauthorizedError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "TokenInvalidError",
    "ForbiddenError",
    # Resource exceptions
    "NotFoundError",
    "ConflictError",
    "AlreadyExistsError",
    "ResourceDeletedError",
    # Validation exceptions
    "ValidationError",
    # File exceptions
    "FileTooLargeError",
    "FileTypeNotAllowedError",
    "BinaryFileNotAllowedError",
    # Rate limiting
    "RateLimitExceededError",
    # Service exceptions
    "ServiceUnavailableError",
    "AIServiceError",
    "ServiceTimeoutError",
    # Internal exceptions
    "InternalError",
    "DatabaseError",
    # Handler functions
    "register_exception_handlers",
    "api_exception_handler",
    "generic_exception_handler",
    "validation_exception_handler",
]
