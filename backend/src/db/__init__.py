"""
Database Package - Database configuration, connections, and session management.

This package provides database connectivity for the AI Code Learning Platform.

Exports:
    DatabaseSettings: Pydantic settings class for database configuration
    get_database_settings: Get cached database settings instance
    get_database_url: Get async database URL (convenience function)
    get_pool_size: Get connection pool size
    get_max_overflow: Get maximum pool overflow
    engine: AsyncEngine - Global async database engine
    async_session_factory: async_sessionmaker - Session factory for creating sessions
    get_db: FastAPI dependency for database sessions
    get_session_context: Async context manager for standalone session usage
    close_db_connection: Function to close all connections on shutdown
"""

from src.db.config import (
    DatabaseSettings,
    get_database_settings,
    get_database_url,
    get_max_overflow,
    get_pool_size,
)
from src.db.session import (
    async_session_factory,
    close_db_connection,
    engine,
    get_db,
    get_session_context,
)

__all__ = [
    "DatabaseSettings",
    "get_database_settings",
    "get_database_url",
    "get_pool_size",
    "get_max_overflow",
    "engine",
    "async_session_factory",
    "get_db",
    "get_session_context",
    "close_db_connection",
]
