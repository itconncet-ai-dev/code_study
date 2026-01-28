"""
Unit Tests for RefreshToken SQLAlchemy Model - T024

TDD RED Phase: These tests define the expected behavior of the RefreshToken model.
All tests should FAIL initially until the model is implemented.

Test Coverage:
- UUID primary key generation
- user_id foreign key (required)
- token_hash field (unique, required)
- expires_at field (required)
- revoked field (default False)
- revoked_at field (nullable)
- Timestamps (created_at)

Reference: data-model.md §RefreshToken entity
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class TestRefreshTokenModel:
    """Test suite for RefreshToken SQLAlchemy model."""

    def test_refresh_token_model_exists(self):
        """RefreshToken model class should be importable from models package."""
        from src.models.refresh_token import RefreshToken

        assert RefreshToken is not None
        assert RefreshToken.__tablename__ == "refresh_tokens"

    def test_refresh_token_has_uuid_primary_key(self):
        """RefreshToken should have a UUID primary key field."""
        from src.models.refresh_token import RefreshToken

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=uuid.uuid4(),
            token_hash="sha256_hash_value_here_for_testing",
            expires_at=expires_at,
        )

        assert token.id is not None
        assert isinstance(token.id, uuid.UUID)

    def test_refresh_token_user_id_required(self):
        """RefreshToken user_id field should be required (not nullable)."""
        from src.models.refresh_token import RefreshToken

        # Creating token without user_id should work at Python level
        # but fail on database constraint
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            token_hash="test_hash",
            expires_at=expires_at,
        )

        # user_id should be None at this point (not yet persisted)
        assert token.user_id is None

    def test_refresh_token_token_hash_required(self):
        """RefreshToken token_hash field should be required."""
        from src.models.refresh_token import RefreshToken

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=uuid.uuid4(),
            expires_at=expires_at,
        )

        # token_hash should be None at this point
        assert token.token_hash is None

    def test_refresh_token_expires_at_required(self):
        """RefreshToken expires_at field should be required."""
        from src.models.refresh_token import RefreshToken

        token = RefreshToken(
            user_id=uuid.uuid4(),
            token_hash="test_hash",
        )

        # expires_at should be None at this point
        assert token.expires_at is None

    def test_refresh_token_revoked_default(self):
        """RefreshToken revoked should default to False."""
        from src.models.refresh_token import RefreshToken

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=uuid.uuid4(),
            token_hash="test_hash",
            expires_at=expires_at,
        )

        assert token.revoked is False

    def test_refresh_token_revoked_at_nullable(self):
        """RefreshToken revoked_at should be nullable."""
        from src.models.refresh_token import RefreshToken

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=uuid.uuid4(),
            token_hash="test_hash",
            expires_at=expires_at,
        )

        assert token.revoked_at is None

    def test_refresh_token_has_created_at_field(self):
        """RefreshToken should have created_at field."""
        from src.models.refresh_token import RefreshToken

        # Check that the model has created_at column defined
        columns = [col.name for col in RefreshToken.__table__.columns]

        assert "created_at" in columns

    def test_refresh_token_model_table_columns(self):
        """RefreshToken model should have all expected columns per data-model.md."""
        from src.models.refresh_token import RefreshToken

        expected_columns = {
            "id",
            "user_id",
            "token_hash",
            "expires_at",
            "created_at",
            "revoked",
            "revoked_at",
        }

        actual_columns = {col.name for col in RefreshToken.__table__.columns}

        assert expected_columns == actual_columns, (
            f"Missing columns: {expected_columns - actual_columns}, "
            f"Extra columns: {actual_columns - expected_columns}"
        )


@pytest.mark.asyncio
class TestRefreshTokenModelDatabase:
    """Database integration tests for RefreshToken model."""

    async def test_refresh_token_create_and_retrieve(self, db_session):
        """RefreshToken should be creatable and retrievable from database."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        # Create a user first (foreign key requirement)
        user = User(
            email="tokentest@example.com",
            password_hash="$2b$12$test_hash_value_here_for_testing",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=user.id,
            token_hash="sha256_unique_hash_for_db_test",
            expires_at=expires_at,
        )

        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)

        # Verify persisted
        assert token.id is not None

        # Retrieve from database
        result = await db_session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == "sha256_unique_hash_for_db_test"
            )
        )
        retrieved_token = result.scalar_one()

        assert retrieved_token.user_id == user.id
        assert retrieved_token.revoked is False
        assert retrieved_token.revoked_at is None

    async def test_refresh_token_hash_unique_constraint(self, db_session):
        """Token hash uniqueness constraint should be enforced at database level."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        # Create a user first
        user = User(
            email="tokenunique@example.com",
            password_hash="hash1",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        token1 = RefreshToken(
            user_id=user.id,
            token_hash="duplicate_hash",
            expires_at=expires_at,
        )
        db_session.add(token1)
        await db_session.commit()

        token2 = RefreshToken(
            user_id=user.id,
            token_hash="duplicate_hash",
            expires_at=expires_at,
        )
        db_session.add(token2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_refresh_token_user_foreign_key(self, db_session):
        """RefreshToken should have valid foreign key to User."""
        from src.models.refresh_token import RefreshToken

        # Create token with non-existent user_id
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=uuid.uuid4(),  # Non-existent user
            token_hash="orphan_token_hash",
            expires_at=expires_at,
        )
        db_session.add(token)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_refresh_token_cascade_delete(self, db_session):
        """RefreshToken should be deleted when parent User is deleted."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        # Create user with token
        user = User(
            email="cascade@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=user.id,
            token_hash="cascade_test_hash",
            expires_at=expires_at,
        )
        db_session.add(token)
        await db_session.commit()
        token_id = token.id

        # Delete user
        await db_session.delete(user)
        await db_session.commit()

        # Token should be deleted via cascade
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.id == token_id)
        )
        assert result.scalar_one_or_none() is None

    async def test_refresh_token_created_at_auto_set(self, db_session):
        """created_at should be automatically set."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        user = User(
            email="timestamp_token@example.com",
            password_hash="test_hash",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=user.id,
            token_hash="timestamp_test_hash",
            expires_at=expires_at,
        )

        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)

        assert token.created_at is not None
        assert isinstance(token.created_at, datetime)

    async def test_refresh_token_revoke(self, db_session):
        """RefreshToken should support revocation with timestamp."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        user = User(
            email="revoke@example.com",
            password_hash="test_hash",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=user.id,
            token_hash="revoke_test_hash",
            expires_at=expires_at,
        )

        db_session.add(token)
        await db_session.commit()
        await db_session.refresh(token)

        # Revoke the token
        token.revoked = True
        token.revoked_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(token)

        assert token.revoked is True
        assert token.revoked_at is not None

    async def test_refresh_token_user_id_not_null_constraint(self, db_session):
        """user_id should have NOT NULL constraint at database level."""
        from src.models.refresh_token import RefreshToken

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            token_hash="no_user_hash",
            expires_at=expires_at,
        )
        db_session.add(token)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_refresh_token_token_hash_not_null_constraint(self, db_session):
        """token_hash should have NOT NULL constraint at database level."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        user = User(
            email="nohash@example.com",
            password_hash="test_hash",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token = RefreshToken(
            user_id=user.id,
            expires_at=expires_at,
        )
        db_session.add(token)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_refresh_token_expires_at_not_null_constraint(self, db_session):
        """expires_at should have NOT NULL constraint at database level."""
        from src.models.refresh_token import RefreshToken
        from src.models.user import User

        user = User(
            email="noexpiry@example.com",
            password_hash="test_hash",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        token = RefreshToken(
            user_id=user.id,
            token_hash="no_expiry_hash",
        )
        db_session.add(token)

        with pytest.raises(IntegrityError):
            await db_session.commit()
