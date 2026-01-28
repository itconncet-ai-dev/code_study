"""
FastAPI Application - AI Code Learning Platform

This module initializes the FastAPI application with all necessary
middleware, CORS configuration, and lifecycle management.

Features:
- CORS middleware with configurable origins from environment
- Request ID middleware for request tracing
- Database connection lifecycle management
- API versioning with /api/v1 prefix
- Health check endpoint

Usage:
    uvicorn backend.src.main:app --reload

Environment Variables:
    CORS_ORIGINS: Comma-separated list of allowed origins
    APP_ENV: Application environment (development/staging/production)
    DEBUG: Enable debug mode
"""

import uuid
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.middleware.base import BaseHTTPMiddleware


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment mode",
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode",
    )
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for application security",
    )

    # Server settings
    backend_host: str = Field(
        default="0.0.0.0",
        description="Backend server host",
    )
    backend_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Backend server port",
    )

    # CORS settings
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        if not self.cors_origins:
            return []
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"


@lru_cache
def get_app_settings() -> AppSettings:
    """
    Get cached application settings instance.

    Returns:
        AppSettings: Cached settings instance
    """
    return AppSettings()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.

    Adds X-Request-ID header to responses for request tracing.
    If the incoming request has X-Request-ID, it will be used;
    otherwise, a new UUID will be generated.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and add request ID."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def run_migrations():
    """Run Alembic migrations on startup to ensure schema is up to date."""
    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations applied successfully.")
    except Exception as e:
        print(f"Migration warning (non-fatal): {e}")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Handles:
    - Database migration (startup)
    - Database connection initialization (startup)
    - Database connection cleanup (shutdown)
    - Any other resource management
    """
    # Startup: Initialize resources
    settings = get_app_settings()
    print(f"Starting AI Code Learning Platform in {settings.app_env} mode...")

    # Run database migrations
    run_migrations()

    yield

    # Shutdown: Cleanup resources
    print("Shutting down AI Code Learning Platform...")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_app_settings()

    # Create FastAPI app with metadata
    app = FastAPI(
        title="AI Code Learning Platform API",
        description=(
            "Backend API for the AI Code Learning Platform. "
            "Provides endpoints for authentication, project management, "
            "code upload, document generation, practice problems, and Q&A."
        ),
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Configure CORS middleware
    cors_origins = settings.cors_origins_list
    if settings.is_development and not cors_origins:
        # Default development origins if none configured
        cors_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
            "http://localhost:3004",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Add request ID middleware for tracing
    app.add_middleware(RequestIDMiddleware)

    # Register health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint for load balancers and monitoring.

        Returns:
            dict: Health status and environment info
        """
        return {
            "status": "healthy",
            "environment": settings.app_env,
            "version": "0.1.0",
        }

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint with API information.

        Returns:
            dict: API information and links
        """
        return {
            "message": "AI Code Learning Platform API",
            "version": "0.1.0",
            "docs": "/docs" if settings.is_development else None,
            "health": "/health",
        }

    # Register exception handlers for consistent error responses
    from .api.exceptions import register_exception_handlers

    register_exception_handlers(app)

    # Include the main API router with versioned prefix
    from .api import api_router

    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    settings = get_app_settings()
    uvicorn.run(
        "backend.src.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.is_development,
    )
