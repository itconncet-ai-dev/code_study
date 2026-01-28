"""
Pytest Configuration and Fixtures

This module provides shared fixtures for all tests in the Code Learning Platform backend.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient


# pytest-asyncio automatically manages event loop in latest versions
# No need to manually create event_loop fixture


# Database fixtures - T010 Implementation
@pytest.fixture
async def db_session() -> AsyncGenerator[Any, None]:
    """
    Provide a database session for tests.

    Creates a new session for each test and rolls back changes
    after the test completes to ensure test isolation.
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.db.session import async_session_factory

    async with async_session_factory() as session:
        try:
            yield session
        finally:
            try:
                await session.rollback()
            except Exception:
                pass


# Test client fixture will be added when main.py is configured (T014)
# @pytest.fixture
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     """Provide an async HTTP client for API tests."""
#     from src.main import app
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as ac:
#         yield ac


# Test user fixtures will be added when auth is implemented (Phase 3)
# @pytest.fixture
# async def test_user() -> dict[str, Any]:
#     """Provide a test user for authenticated requests."""
#     pass
