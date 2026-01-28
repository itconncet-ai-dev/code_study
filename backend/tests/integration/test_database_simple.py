"""
Simple Database Integration Tests

Straightforward tests for database connection and basic operations.
"""

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseIntegration:
    """Basic database integration tests."""

    @pytest.mark.asyncio
    async def test_01_connection(self, db_session: AsyncSession):
        """Test database connection works."""
        result = await db_session.execute(select(func.now()))
        current_time = result.scalar()
        assert current_time is not None
        print(f"[OK] Database connected at {current_time}")

    @pytest.mark.asyncio
    async def test_02_simple_select(self, db_session: AsyncSession):
        """Test simple SELECT query."""
        result = await db_session.execute(select(func.literal(42)))
        value = result.scalar()
        assert value == 42
        print(f"[OK] Simple SELECT: 42 = {value}")

    @pytest.mark.asyncio
    async def test_03_basic_math(self, db_session: AsyncSession):
        """Test basic SQL math."""
        result = await db_session.execute(select(func.literal(10 + 20)))
        value = result.scalar()
        assert value == 30
        print(f"[OK] Math: 10 + 20 = {value}")

    @pytest.mark.asyncio
    async def test_04_string_operations(self, db_session: AsyncSession):
        """Test string operations."""
        result = await db_session.execute(select(func.upper(func.literal("hello"))))
        value = result.scalar()
        assert value == "HELLO"
        print(f"[OK] String function: UPPER('hello') = {value}")

    @pytest.mark.asyncio
    async def test_05_cast_operations(self, db_session: AsyncSession):
        """Test type casting."""
        result = await db_session.execute(
            select(func.cast(func.literal("123"), type_=int))
        )
        value = result.scalar()
        assert value == 123
        print(f"[OK] Cast string to int: '123' = {value}")

    @pytest.mark.asyncio
    async def test_06_multiple_columns(self, db_session: AsyncSession):
        """Test selecting multiple columns."""
        result = await db_session.execute(
            select(func.literal("col1"), func.literal("col2"), func.literal(42))
        )
        row = result.tuple()
        assert row == ("col1", "col2", 42)
        print(f"[OK] Multiple columns: {row}")

    @pytest.mark.asyncio
    async def test_07_aggregate_function(self, db_session: AsyncSession):
        """Test aggregate functions."""
        # Create a VALUES clause to test aggregation
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM (VALUES (1), (2), (3)) AS t(n)")
        )
        count = result.scalar()
        assert count == 3
        print(f"[OK] COUNT aggregate: {count}")

    @pytest.mark.asyncio
    async def test_08_null_handling(self, db_session: AsyncSession):
        """Test NULL handling."""
        result = await db_session.execute(
            select(func.coalesce(None, func.literal("default")))
        )
        value = result.scalar()
        assert value == "default"
        print(f"[OK] COALESCE(NULL, 'default') = {value}")

    @pytest.mark.asyncio
    async def test_09_case_expression(self, db_session: AsyncSession):
        """Test CASE expression."""
        from sqlalchemy import case

        expr = case((func.literal(1) == 1, "one"), else_="other")
        result = await db_session.execute(select(expr))
        value = result.scalar()
        assert value == "one"
        print(f"[OK] CASE expression: {value}")

    @pytest.mark.asyncio
    async def test_10_commit_works(self, db_session: AsyncSession):
        """Test that commit works without error."""
        # Just verify commit doesn't raise
        await db_session.commit()
        print("[OK] Commit executed successfully")


class TestConnectionPooling:
    """Test connection pooling."""

    @pytest.mark.asyncio
    async def test_pool_info(self):
        """Test connection pool statistics."""
        from src.db import engine

        pool = engine.pool
        assert pool is not None
        # Just verify pool exists and can be accessed
        print(f"[OK] Connection pool: {type(pool).__name__}")

    @pytest.mark.asyncio
    async def test_multiple_sessions(self):
        """Test creating multiple sessions."""
        from src.db.session import get_session_context

        # Create first session
        async with get_session_context() as session1:
            result1 = await session1.execute(select(func.literal(1)))
            val1 = result1.scalar()

        # Create second session
        async with get_session_context() as session2:
            result2 = await session2.execute(select(func.literal(2)))
            val2 = result2.scalar()

        assert val1 == 1
        assert val2 == 2
        print(f"[OK] Multiple sessions: {val1}, {val2}")

    @pytest.mark.asyncio
    async def test_nested_queries(self, db_session: AsyncSession):
        """Test nested queries."""
        # SELECT 1 + (SELECT 2)
        result = await db_session.execute(
            select(func.literal(1) + select(func.literal(2)).scalar_subquery())
        )
        value = result.scalar()
        assert value == 3
        print(f"[OK] Nested query: 1 + (SELECT 2) = {value}")
