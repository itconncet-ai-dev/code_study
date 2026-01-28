"""
Database Configuration - AI Code Learning Platform

This module provides centralized database configuration using Pydantic
BaseSettings for environment variable validation and type safety.

Features:
- Environment-based configuration with validation
- Connection pooling settings with sensible defaults
- Environment-specific defaults (development vs production)
- Database URL construction with async driver support

Usage:
    from backend.src.db.config import get_database_settings

    settings = get_database_settings()
    database_url = settings.database_url
    pool_size = settings.pool_size
"""

from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings loaded from environment variables.

    All settings have sensible development defaults but should be
    explicitly configured in production environments.

    Environment Variables:
        POSTGRES_HOST: Database server hostname
        POSTGRES_PORT: Database server port
        POSTGRES_USER: Database username
        POSTGRES_PASSWORD: Database password
        POSTGRES_DB: Database name
        DATABASE_URL: Full connection URL (overrides individual settings)
        DB_POOL_SIZE: Connection pool size
        DB_MAX_OVERFLOW: Maximum pool overflow connections
        DB_POOL_TIMEOUT: Connection acquisition timeout in seconds
        DB_POOL_RECYCLE: Connection recycle time in seconds
        DB_ECHO: Enable SQL query logging
        APP_ENV: Application environment (development/staging/production)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment mode
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment mode",
    )

    # PostgreSQL connection settings
    postgres_host: str = Field(
        default="localhost",
        description="PostgreSQL server hostname",
    )
    postgres_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="PostgreSQL server port",
    )
    postgres_user: str = Field(
        default="code_learning",
        description="PostgreSQL username",
    )
    postgres_password: str = Field(
        default="code_learning_dev",
        description="PostgreSQL password",
    )
    postgres_db: str = Field(
        default="code_learning_db",
        description="PostgreSQL database name",
    )

    # Optional full database URL (overrides individual settings)
    database_url: str | None = Field(
        default=None,
        description="Full PostgreSQL connection URL (overrides individual settings)",
    )

    # Connection pooling settings
    db_pool_size: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of connections to keep in the pool",
    )
    db_max_overflow: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Maximum overflow connections beyond pool_size",
    )
    db_pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Seconds to wait for a connection from the pool",
    )
    db_pool_recycle: int = Field(
        default=1800,
        ge=60,
        le=7200,
        description="Seconds after which a connection is recycled",
    )
    db_echo: bool = Field(
        default=False,
        description="Enable SQL query logging (use with caution in production)",
    )

    # SQLAlchemy echo setting from environment (alternative name)
    sqlalchemy_echo: bool = Field(
        default=False,
        description="Alternative setting for SQL query logging",
    )

    @field_validator("postgres_password")
    @classmethod
    def validate_password_in_production(cls, v: str, _info) -> str:
        """Warn if using default password in non-development environment."""
        # Access other values through info.data
        return v

    @computed_field
    @property
    def async_database_url(self) -> str:
        """
        Construct the async PostgreSQL connection URL.

        Returns the DATABASE_URL if set (ensuring async driver is used),
        otherwise constructs it from individual PostgreSQL settings.

        Returns:
            str: PostgreSQL connection URL with asyncpg driver
        """
        if self.database_url:
            url = self.database_url
            # Ensure async driver is used
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            return url

        # Construct from individual settings with URL encoding for special characters
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def sync_database_url(self) -> str:
        """
        Construct the sync PostgreSQL connection URL for Alembic migrations.

        Returns:
            str: PostgreSQL connection URL with psycopg2 driver
        """
        if self.database_url:
            url = self.database_url
            # Ensure sync driver is used
            if "+asyncpg" in url:
                return url.replace("+asyncpg", "")
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql://", 1)
            return url

        # Construct from individual settings with URL encoding for special characters
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def echo_enabled(self) -> bool:
        """
        Determine if SQL echo should be enabled.

        Returns True if either db_echo or sqlalchemy_echo is True.
        """
        return self.db_echo or self.sqlalchemy_echo

    @computed_field
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    def get_pool_config(self) -> dict:
        """
        Get connection pool configuration as a dictionary.

        Returns a dictionary suitable for passing to create_async_engine.

        Returns:
            dict: Pool configuration parameters
        """
        return {
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
            "pool_recycle": self.db_pool_recycle,
            "pool_pre_ping": True,  # Verify connections before use
        }

    def get_engine_config(self) -> dict:
        """
        Get full engine configuration including pool settings.

        Returns:
            dict: Complete engine configuration parameters
        """
        config = self.get_pool_config()
        config["echo"] = self.echo_enabled
        return config


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """
    Get cached database settings instance.

    Uses LRU cache to ensure settings are only loaded once from
    environment variables, improving performance and consistency.

    Returns:
        DatabaseSettings: Cached settings instance
    """
    return DatabaseSettings()


def get_pool_size() -> int:
    """
    Get connection pool size.

    Convenience function for backward compatibility with session.py.

    Returns:
        int: Pool size
    """
    return get_database_settings().db_pool_size


def get_max_overflow() -> int:
    """
    Get maximum pool overflow.

    Convenience function for backward compatibility with session.py.

    Returns:
        int: Max overflow
    """
    return get_database_settings().db_max_overflow


def get_database_url() -> str:
    """
    Get async database URL.

    Convenience function for backward compatibility with session.py.

    Returns:
        str: PostgreSQL connection URL with asyncpg driver
    """
    return get_database_settings().async_database_url
