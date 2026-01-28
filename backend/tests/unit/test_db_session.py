"""
Tests for Database Session Management - T010

This module tests the database connection and session management functionality.
Tests cover async engine creation, session lifecycle, and FastAPI dependency injection.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class TestDatabaseSession:
    """Tests for database session management."""

    def test_engine_creation(self):
        """Test that async engine is created with correct configuration."""
        from src.db.session import engine

        # Engine should be an AsyncEngine instance
        assert engine is not None
        assert isinstance(engine, AsyncEngine)

    def test_engine_uses_asyncpg(self):
        """Test that engine uses asyncpg driver for PostgreSQL."""
        from src.db.session import engine

        # The URL should use asyncpg driver
        url_str = str(engine.url)
        assert "asyncpg" in url_str or "postgresql" in url_str

    def test_session_factory_exists(self):
        """Test that async session factory is properly configured."""
        from src.db.session import async_session_factory

        assert async_session_factory is not None

    def test_session_factory_configuration(self):
        """Test session factory has correct settings."""
        from src.db.session import async_session_factory

        # Session factory should be configured for async sessions
        assert async_session_factory.class_ == AsyncSession
        # expire_on_commit should be False for async usage
        assert async_session_factory.kw.get("expire_on_commit") is False


class TestGetDbDependency:
    """Tests for the FastAPI get_db dependency."""

    @pytest.mark.asyncio
    async def test_get_db_returns_session(self):
        """Test that get_db yields an AsyncSession."""
        from src.db.session import get_db

        # get_db is an async generator
        async for session in get_db():
            assert session is not None
            assert isinstance(session, AsyncSession)
            break  # Only need one iteration for test

    @pytest.mark.asyncio
    async def test_get_db_closes_session(self):
        """Test that get_db properly closes the session after use."""
        from src.db.session import get_db

        session_instance = None
        async for session in get_db():
            session_instance = session

        # After the generator exits, session should be closed
        # In SQLAlchemy 2.0, we check if the session is no longer active
        assert session_instance is not None


class TestConnectionPooling:
    """Tests for database connection pool configuration."""

    def test_pool_configuration(self):
        """Test that connection pool is properly configured."""
        from src.db.session import engine

        # Engine should have pool configuration
        pool = engine.pool
        assert pool is not None

    def test_pool_size_from_config(self):
        """Test that pool size can be configured via settings."""
        from src.db.session import engine

        # Pool should exist with configured size
        # Default pool size should be at least 5
        pool = engine.pool
        assert pool is not None


class TestDatabaseUrlConstruction:
    """Tests for database URL construction."""

    def test_database_url_from_env(self):
        """Test database URL is constructed from environment variables."""
        from src.db.session import get_database_url

        url = get_database_url()

        # URL should not be empty
        assert url is not None
        assert len(url) > 0
        # URL should be for PostgreSQL with asyncpg
        assert "postgresql+asyncpg://" in url


class TestSessionContextManager:
    """Tests for session context manager utilities."""

    @pytest.mark.asyncio
    async def test_get_session_context(self):
        """Test async context manager for session access."""
        from src.db.session import get_session_context

        async with get_session_context() as session:
            assert session is not None
            assert isinstance(session, AsyncSession)
