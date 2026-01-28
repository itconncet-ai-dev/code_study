"""
Unit Tests for User SQLAlchemy Model - T023

TDD RED Phase: These tests define the expected behavior of the User model.
All tests should FAIL initially until the model is implemented.

Test Coverage:
- UUID primary key generation
- Email field validation (unique, required)
- Password hash storage
- skill_level default value
- Timestamps (created_at, updated_at)
- last_login_at nullable field
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class TestUserModel:
    """Test suite for User SQLAlchemy model."""

    def test_user_model_exists(self):
        """User model class should be importable from models package."""
        from src.models.user import User

        assert User is not None
        assert User.__tablename__ == "users"

    def test_user_has_uuid_primary_key(self):
        """User should have a UUID primary key field."""
        from src.models.user import User

        user = User(
            email="test@example.com",
            password_hash="hashed_password_123"
        )

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)

    def test_user_email_required(self):
        """User email field should be required (not nullable)."""
        from src.models.user import User

        # Creating user without email should work at Python level
        # but fail on database constraint
        user = User(password_hash="hashed_password_123")

        # email should be None at this point (not yet persisted)
        assert user.email is None

    def test_user_password_hash_required(self):
        """User password_hash field should be required."""
        from src.models.user import User

        user = User(email="test@example.com")

        # password_hash should be None at this point
        assert user.password_hash is None

    def test_user_skill_level_default(self):
        """User skill_level should default to 'Complete Beginner'."""
        from src.models.user import User

        user = User(
            email="test@example.com",
            password_hash="hashed_password_123"
        )

        assert user.skill_level == "Complete Beginner"

    def test_user_last_login_at_nullable(self):
        """User last_login_at should be nullable."""
        from src.models.user import User

        user = User(
            email="test@example.com",
            password_hash="hashed_password_123"
        )

        assert user.last_login_at is None

    def test_user_has_timestamp_fields(self):
        """User should have created_at and updated_at fields via TimestampMixin."""
        from src.models.user import User

        # Check that the model has timestamp columns defined
        columns = [col.name for col in User.__table__.columns]

        assert "created_at" in columns
        assert "updated_at" in columns

    def test_user_model_table_columns(self):
        """User model should have all expected columns per data-model.md."""
        from src.models.user import User

        expected_columns = {
            "id",
            "email",
            "password_hash",
            "skill_level",
            "created_at",
            "updated_at",
            "last_login_at",
        }

        actual_columns = {col.name for col in User.__table__.columns}

        assert expected_columns == actual_columns, (
            f"Missing columns: {expected_columns - actual_columns}, "
            f"Extra columns: {actual_columns - expected_columns}"
        )


@pytest.mark.asyncio
class TestUserModelDatabase:
    """Database integration tests for User model."""

    async def test_user_create_and_retrieve(self, db_session):
        """User should be creatable and retrievable from database."""
        from src.models.user import User

        user = User(
            email="dbtest@example.com",
            password_hash="$2b$12$test_hash_value_here_for_testing"
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Verify persisted
        assert user.id is not None

        # Retrieve from database
        result = await db_session.execute(
            select(User).where(User.email == "dbtest@example.com")
        )
        retrieved_user = result.scalar_one()

        assert retrieved_user.email == "dbtest@example.com"
        assert retrieved_user.skill_level == "Complete Beginner"

    async def test_user_email_unique_constraint(self, db_session):
        """Email uniqueness constraint should be enforced at database level."""
        from src.models.user import User

        user1 = User(
            email="duplicate@example.com",
            password_hash="hash1"
        )
        db_session.add(user1)
        await db_session.commit()

        user2 = User(
            email="duplicate@example.com",
            password_hash="hash2"
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_user_timestamps_auto_set(self, db_session):
        """created_at and updated_at should be automatically set."""
        from src.models.user import User

        user = User(
            email="timestamp@example.com",
            password_hash="test_hash"
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    async def test_user_email_not_null_constraint(self, db_session):
        """Email should have NOT NULL constraint at database level."""
        from src.models.user import User

        user = User(password_hash="test_hash")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_user_password_hash_not_null_constraint(self, db_session):
        """Password hash should have NOT NULL constraint at database level."""
        from src.models.user import User

        user = User(email="nopassword@example.com")
        db_session.add(user)

        with pytest.raises(IntegrityError):
            await db_session.commit()
