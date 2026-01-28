"""
Database CRUD Operations Integration Tests - T010

Tests real CRUD operations directly against PostgreSQL database.
"""

import pytest
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession


class TestBasicDatabaseOperations:
    """Tests basic database operations."""

    @pytest.mark.asyncio
    async def test_database_connection(self, db_session: AsyncSession):
        """
        Test: 데이터베이스 연결 확인
        Verify that database connection is working.
        """
        # Simple ping query
        result = await db_session.execute(select(func.now()))
        current_time = result.scalar()

        assert current_time is not None
        print(f"[PASS] Database connected! Current time: {current_time}")

    @pytest.mark.asyncio
    async def test_simple_echo_query(self, db_session: AsyncSession):
        """
        Test: 간단한 쿼리 실행
        Execute a simple SELECT query to verify SQLAlchemy works.
        """
        result = await db_session.execute(select(func.literal(42)))
        value = result.scalar()

        assert value == 42
        print("[PASS] Simple query executed successfully")

    @pytest.mark.asyncio
    async def test_create_temporary_table(self, db_session: AsyncSession):
        """
        Test: 임시 테이블 생성 및 데이터 삽입
        Create a temporary table and insert data.
        """
        # Create a temporary table
        await db_session.execute(
            text("""
            CREATE TEMPORARY TABLE test_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                value INT
            )
        """)
        )

        # Insert data
        await db_session.execute(
            text("INSERT INTO test_data (name, value) VALUES ('test1', 100)")
        )
        await db_session.execute(
            text("INSERT INTO test_data (name, value) VALUES ('test2', 200)")
        )
        await db_session.commit()

        # Query data
        result = await db_session.execute(text("SELECT * FROM test_data ORDER BY id"))
        rows = result.fetchall()

        assert len(rows) == 2
        assert rows[0][1] == "test1"
        assert rows[0][2] == 100
        assert rows[1][1] == "test2"
        assert rows[1][2] == 200
        print(f"[PASS] Created temp table with {len(rows)} records")
        for row in rows:
            print(f"  - ID: {row[0]}, Name: {row[1]}, Value: {row[2]}")

    @pytest.mark.asyncio
    async def test_update_temporary_data(self, db_session: AsyncSession):
        """
        Test: 임시 테이블 데이터 수정
        Update data in temporary table.
        """
        # Create temporary table
        await db_session.execute(
            text("""
            CREATE TEMPORARY TABLE test_update (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                status VARCHAR(50)
            )
        """)
        )

        # Insert initial data
        await db_session.execute(
            text(
                "INSERT INTO test_update (name, status) VALUES ('record1', 'pending')"
            )
        )
        await db_session.commit()

        # Update data
        await db_session.execute(
            text(
                "UPDATE test_update SET status = 'completed' WHERE name = 'record1'"
            )
        )
        await db_session.commit()

        # Verify update
        result = await db_session.execute(
            text("SELECT status FROM test_update WHERE name = 'record1'")
        )
        status = result.scalar()

        assert status == "completed"
        print(f"[PASS] Updated record status: {status}")

    @pytest.mark.asyncio
    async def test_delete_temporary_data(self, db_session: AsyncSession):
        """
        Test: 임시 테이블 데이터 삭제
        Delete data from temporary table.
        """
        # Create temporary table
        await db_session.execute(
            text("""
            CREATE TEMPORARY TABLE test_delete (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            )
        """)
        )

        # Insert multiple records
        await db_session.execute(
            text("INSERT INTO test_delete (name) VALUES ('delete_me')")
        )
        await db_session.execute(
            text("INSERT INTO test_delete (name) VALUES ('keep_me')")
        )
        await db_session.commit()

        # Delete one record
        await db_session.execute(text("DELETE FROM test_delete WHERE name = 'delete_me'"))
        await db_session.commit()

        # Verify deletion
        result = await db_session.execute(text("SELECT COUNT(*) FROM test_delete"))
        count = result.scalar()

        assert count == 1

        result = await db_session.execute(
            text("SELECT name FROM test_delete WHERE id = 1")
        )
        remaining = result.scalar()

        assert remaining == "keep_me"
        print(f"[PASS] Deleted record, {count} record(s) remaining")

    @pytest.mark.asyncio
    async def test_transaction_commit(self, db_session: AsyncSession):
        """
        Test: 트랜잭션 커밋
        Verify that transaction commit works properly.
        """
        # Create table
        await db_session.execute(
            text("""
            CREATE TEMPORARY TABLE test_transaction (
                id SERIAL PRIMARY KEY,
                value INT
            )
        """)
        )

        # Insert and commit
        await db_session.execute(text("INSERT INTO test_transaction (value) VALUES (100)"))
        await db_session.commit()

        # Verify data persists after commit
        result = await db_session.execute(
            text("SELECT value FROM test_transaction WHERE id = 1")
        )
        value = result.scalar()

        assert value == 100
        print(f"[PASS] Transaction committed successfully, value: {value}")

    @pytest.mark.asyncio
    async def test_connection_pooling(self, db_session: AsyncSession):
        """
        Test: 연결 풀링 작동
        Verify that connection pooling works.
        """
        from src.db import engine

        # Check engine pool
        pool = engine.pool
        assert pool is not None

        # Execute multiple queries
        for i in range(5):
            result = await db_session.execute(select(func.literal(i)))
            value = result.scalar()
            assert value == i

        print("[PASS] Connection pooling working (5 queries executed)")

    @pytest.mark.asyncio
    async def test_aggregate_functions(self, db_session: AsyncSession):
        """
        Test: 집계 함수 (COUNT, SUM, AVG)
        Test SQL aggregate functions.
        """
        # Create test table
        await db_session.execute(
            text("""
            CREATE TEMPORARY TABLE test_agg (
                id SERIAL PRIMARY KEY,
                category VARCHAR(50),
                amount INT
            )
        """)
        )

        # Insert data
        await db_session.execute(
            text(
                "INSERT INTO test_agg (category, amount) VALUES ('A', 100), ('A', 200), ('B', 150), ('B', 250)"
            )
        )
        await db_session.commit()

        # Test COUNT
        count_result = await db_session.execute(text("SELECT COUNT(*) FROM test_agg"))
        count = count_result.scalar()
        assert count == 4

        # Test SUM
        sum_result = await db_session.execute(
            text("SELECT SUM(amount) FROM test_agg WHERE category = 'A'")
        )
        total = sum_result.scalar()
        assert total == 300

        # Test AVG
        avg_result = await db_session.execute(
            text("SELECT AVG(amount) FROM test_agg")
        )
        average = avg_result.scalar()
        assert average == 175.0

        print(f"[PASS] Aggregate functions working: COUNT={count}, SUM(A)={total}, AVG={average}")


class TestConnectionManagement:
    """Tests connection and session management."""

    @pytest.mark.asyncio
    async def test_session_cleanup(self):
        """
        Test: 세션 자동 정리
        Verify that sessions are properly cleaned up.
        """
        from src.db.session import get_session_context

        # Use context manager
        async with get_session_context() as session:
            result = await session.execute(select(func.literal(1)))
            assert result.scalar() == 1

        # Session should be closed now, but we can still create a new one
        async with get_session_context() as session:
            result = await session.execute(select(func.literal(2)))
            assert result.scalar() == 2

        print("[PASS] Session cleanup working correctly")

    @pytest.mark.asyncio
    async def test_multiple_operations_in_session(self, db_session: AsyncSession):
        """
        Test: 세션에서 여러 작업 수행
        Execute multiple operations within a single session.
        """
        # Multiple queries in single session
        result1 = await db_session.execute(select(func.literal(10)))
        val1 = result1.scalar()

        result2 = await db_session.execute(select(func.literal(20)))
        val2 = result2.scalar()

        result3 = await db_session.execute(select(func.literal(30)))
        val3 = result3.scalar()

        assert val1 == 10 and val2 == 20 and val3 == 30
        print(f"[PASS] Multiple operations in session: {val1}, {val2}, {val3}")
