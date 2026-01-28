"""
Database Session Management - AI Code Learning Platform

This module provides async database connection and session management using
SQLAlchemy 2.0+ with asyncpg driver for PostgreSQL.

Features:
- Async engine with connection pooling
- Async session factory for FastAPI dependency injection
- Context manager for standalone session usage
- Environment-based configuration via config.py

Usage:
    # In FastAPI endpoints (dependency injection)
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        return result.scalars().all()

    # In standalone scripts or services
    async with get_session_context() as session:
        result = await session.execute(select(User))
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.db.config import get_database_settings


def create_engine() -> AsyncEngine:
    """
    Create and configure the async SQLAlchemy engine.

    The engine is configured with:
    - asyncpg driver for async PostgreSQL operations
    - Connection pooling with configurable size from config.py
    - Echo disabled by default (enable via DB_ECHO=true or SQLALCHEMY_ECHO=true)

    Returns:
        AsyncEngine: Configured async database engine
    """
    settings = get_database_settings()

    return create_async_engine(
        settings.async_database_url,
        **settings.get_engine_config(),
    )


# Global engine instance - created once at module load
engine: AsyncEngine = create_engine()

# Async session factory with proper configuration for async operations
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Required for async - don't expire objects after commit
    autoflush=True,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.

    Yields an async database session that is automatically closed
    after the request completes. Use with FastAPI's Depends():

    Example:
        @app.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session for the current request
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database session access.

    Use this for standalone scripts, background tasks, or any code
    outside of FastAPI request handlers where dependency injection
    isn't available.

    Example:
        async with get_session_context() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()

    Yields:
        AsyncSession: Database session for the context
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_connection() -> None:
    """
    Close all database connections.

    Call this during application shutdown to properly dispose
    of all pooled connections.

    Example:
        @app.on_event("shutdown")
        async def shutdown():
            await close_db_connection()
    """
    await engine.dispose()
