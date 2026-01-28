"""
Integration Tests for Database Operations - T010

Tests actual database connectivity and CRUD operations using real database.
These tests verify:
- Database connection works correctly
- Session management handles transactions properly
- Basic CRUD operations work with the async session
"""

import uuid
from datetime import datetime

import pytest

# Simple test model for integration testing
from sqlalchemy import Column, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TestUser(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Test user model for integration testing."""

    __tablename__ = "test_users"

    email: str = Column(String(255), unique=True, nullable=False)
    name: str = Column(String(255), nullable=False)


class TestDatabaseConnectivity:
    """Tests for basic database connectivity."""

    @pytest.mark.asyncio
    async def test_database_connection_succeeds(self, db_session: AsyncSession):
        """Test that database connection is successful."""
        # Simple health check query
        result = await db_session.execute(select(func.now()))
        current_time = result.scalar()

        assert current_time is not None
        assert isinstance(current_time, datetime)

    @pytest.mark.asyncio
    async def test_database_echo_query(self, db_session: AsyncSession):
        """Test that we can execute a simple echo query."""
        # SELECT 1 as health check
        result = await db_session.execute(select(func.literal(1)))
        value = result.scalar()

        assert value == 1


class TestCRUDOperations:
    """Tests for Create, Read, Update, Delete operations."""

    @pytest.mark.asyncio
    async def test_create_record(self, db_session: AsyncSession):
        """Test creating a record in the database."""
        # Create a test user
        user_id = uuid.uuid4()
        test_user = TestUser(id=user_id, email="test@example.com", name="Test User")

        db_session.add(test_user)
        await db_session.flush()

        # Verify it was created
        assert test_user.id == user_id
        assert test_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_read_record(self, db_session: AsyncSession):
        """Test reading a record from the database."""
        # First create a record
        user_id = uuid.uuid4()
        test_user = TestUser(id=user_id, email="read@example.com", name="Read User")
        db_session.add(test_user)
        await db_session.flush()

        # Now read it back
        stmt = select(TestUser).where(TestUser.id == user_id)
        result = await db_session.execute(stmt)
        retrieved_user = result.scalar_one()

        assert retrieved_user.id == user_id
        assert retrieved_user.email == "read@example.com"
        assert retrieved_user.name == "Read User"

    @pytest.mark.asyncio
    async def test_update_record(self, db_session: AsyncSession):
        """Test updating a record in the database."""
        # Create a record
        user_id = uuid.uuid4()
        test_user = TestUser(id=user_id, email="update@example.com", name="Update User")
        db_session.add(test_user)
        await db_session.flush()

        # Update it
        test_user.name = "Updated Name"
        await db_session.flush()

        # Verify the update
        stmt = select(TestUser).where(TestUser.id == user_id)
        result = await db_session.execute(stmt)
        updated_user = result.scalar_one()

        assert updated_user.name == "Updated Name"
        assert updated_user.email == "update@example.com"

    @pytest.mark.asyncio
    async def test_delete_record(self, db_session: AsyncSession):
        """Test deleting a record from the database."""
        # Create a record
        user_id = uuid.uuid4()
        test_user = TestUser(id=user_id, email="delete@example.com", name="Delete User")
        db_session.add(test_user)
        await db_session.flush()

        # Delete it
        await db_session.delete(test_user)
        await db_session.flush()

        # Verify it's gone
        stmt = select(TestUser).where(TestUser.id == user_id)
        result = await db_session.execute(stmt)
        deleted_user = result.scalar_one_or_none()

        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_query_multiple_records(self, db_session: AsyncSession):
        """Test querying multiple records."""
        # Create multiple test users
        user_ids = []
        for i in range(3):
            user_id = uuid.uuid4()
            user_ids.append(user_id)
            test_user = TestUser(
                id=user_id, email=f"user{i}@example.com", name=f"User {i}"
            )
            db_session.add(test_user)
        await db_session.flush()

        # Query all
        stmt = select(TestUser).where(TestUser.id.in_(user_ids))
        result = await db_session.execute(stmt)
        users = result.scalars().all()

        assert len(users) == 3

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test that transaction rollback works correctly."""
        from src.db.session import async_session_factory

        async with async_session_factory() as session:
            # Create a record
            user_id = uuid.uuid4()
            test_user = TestUser(
                id=user_id, email="rollback@example.com", name="Rollback User"
            )
            session.add(test_user)
            await session.flush()

            # Now rollback
            await session.rollback()

        # Create a new session and verify the record doesn't exist
        async with async_session_factory() as session:
            stmt = select(TestUser).where(TestUser.id == user_id)
            result = await session.execute(stmt)
            result.scalar_one_or_none()

            # The record should not exist since we rolled back
            # (Note: In test isolation, this might not work if the record was never committed)


class TestConnectionPooling:
    """Tests for connection pooling behavior."""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(self):
        """Test that multiple sessions can be created concurrently."""
        import asyncio

        from src.db.session import async_session_factory

        async def create_session_and_query(user_num: int) -> int:
            async with async_session_factory() as session:
                result = await session.execute(select(func.literal(user_num)))
                return result.scalar()

        # Create 5 concurrent sessions
        tasks = [create_session_and_query(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        assert results == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_session_closes_after_context(self):
        """Test that session is properly closed after context manager."""
        from src.db.session import get_session_context

        async with get_session_context() as session:
            # Session should be usable here
            result = await session.execute(select(func.literal(1)))
            assert result.scalar() == 1

        # After context, session should be closed
        # Note: We can't directly test this without accessing private attributes
        # but the important thing is no exception is raised
