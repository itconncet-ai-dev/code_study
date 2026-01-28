"""
SQLAlchemy Base Model - AI Code Learning Platform

This module provides the declarative base class and common mixins for all
database models. All entity models should inherit from Base to ensure
proper integration with Alembic migrations and SQLAlchemy ORM.

Usage:
    from src.models.base import Base

    class User(Base):
        __tablename__ = "users"
        id = Column(UUID, primary_key=True)
        ...
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class for all ORM models.

    All database models should inherit from this class to:
    - Enable Alembic migration autogeneration
    - Provide consistent model configuration
    - Support async database operations

    Example:
        class User(Base):
            __tablename__ = "users"
            id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            email: Mapped[str] = mapped_column(unique=True, nullable=False)
    """

    # Type annotation map for Python types to SQLAlchemy types
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        datetime: DateTime(timezone=True),
    }


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timestamp columns.

    Automatically sets created_at on insert and updates updated_at
    on every update using database-side triggers.

    Usage:
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            id = Column(UUID, primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin providing soft delete functionality with 30-day trash retention.

    Adds columns for tracking deletion status and scheduled permanent deletion.
    Items can be restored from trash within 30 days.

    Columns:
        deletion_status: 'active' or 'trashed'
        trashed_at: When item was moved to trash
        scheduled_deletion_at: When item will be permanently deleted (trashed_at + 30 days)

    Usage:
        class Project(Base, SoftDeleteMixin):
            __tablename__ = "projects"
            id = Column(UUID, primary_key=True)

    Business Rules:
        - Default status is 'active'
        - When trashed, set trashed_at and scheduled_deletion_at
        - Scheduled cleanup job permanently deletes items past scheduled_deletion_at
        - Restore clears trashed_at and scheduled_deletion_at, sets status to 'active'
    """

    deletion_status: Mapped[str] = mapped_column(
        default="active",
        nullable=False,
        index=True,
    )
    trashed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    scheduled_deletion_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class UUIDPrimaryKeyMixin:
    """
    Mixin providing a UUID primary key column.

    Uses PostgreSQL's UUID type with auto-generation via Python's uuid4.
    All entity models should use UUIDs for primary keys per data model spec.

    Usage:
        class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
            __tablename__ = "users"
            email = Column(String, unique=True, nullable=False)
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


def model_to_dict(model: Any, exclude: set[str] | None = None) -> dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to a dictionary.

    Useful for serialization and API responses. Excludes internal
    SQLAlchemy attributes (those starting with '_').

    Args:
        model: SQLAlchemy model instance
        exclude: Optional set of column names to exclude from output

    Returns:
        Dictionary representation of the model

    Example:
        user = session.get(User, user_id)
        user_dict = model_to_dict(user, exclude={"password_hash"})
    """
    exclude = exclude or set()
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
        if column.name not in exclude
    }
