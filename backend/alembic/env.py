"""
Alembic Environment Configuration - AI Code Learning Platform

This module configures Alembic for database migrations with:
- SQLAlchemy database connection support (sync mode for migrations)
- Automatic migration script generation from model changes
- Environment variable configuration loading
- Both online and offline migration modes
"""

import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from alembic import context

# Add the backend source directory to Python path for model imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
# Check both backend directory and project root
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Try project root
    project_root_env = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    if os.path.exists(project_root_env):
        load_dotenv(project_root_env)

# Alembic Config object - provides access to values in alembic.ini
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the SQLAlchemy declarative base for autogenerate support
# NOTE: This import must be after adding src to sys.path
# Import all models here for Alembic to detect them for autogenerate
# Future models should be imported here as they are created
try:
    from src.models.base import Base

    target_metadata = Base.metadata
except ImportError:
    # If models are not yet created, use None
    # This allows alembic commands to work before models exist
    target_metadata = None


def get_database_url() -> str:
    """
    Get the database URL from environment variables.

    The DATABASE_URL uses asyncpg driver (postgresql+asyncpg://...)
    but Alembic requires the sync driver (postgresql://...).
    This function handles the conversion.

    Returns:
        str: Database URL with sync driver for Alembic
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        # Construct from individual environment variables
        host = os.environ.get("POSTGRES_HOST", "localhost")
        port = os.environ.get("POSTGRES_PORT", "5432")
        user = os.environ.get("POSTGRES_USER", "code_learning")
        password = os.environ.get("POSTGRES_PASSWORD", "code_learning_dev")
        db_name = os.environ.get("POSTGRES_DB", "code_learning_db")
        database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    # Convert async driver to sync driver for Alembic operations
    # Alembic migrations run synchronously
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )
    elif database_url.startswith("postgresql://"):
        # Standard postgres URL, convert to psycopg2 explicitly
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg2://", 1
        )

    return database_url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Offline mode generates SQL scripts without connecting to the database.
    This is useful for:
    - Generating SQL files for review before applying
    - Environments where direct database access is restricted
    - Database-as-code workflows

    Usage:
        alembic upgrade head --sql > migration.sql
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Execute migrations within the provided connection context.

    This is called by both sync and async migration paths.

    Args:
        connection: Active database connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
        include_schemas=True,  # Include schema in autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Online mode connects directly to the database and applies migrations.
    This is the standard mode for development and production deployments.

    Usage:
        alembic upgrade head
        alembic downgrade -1
    """
    # Update configuration with database URL
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    # Create sync engine for migration
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


# Determine which mode to run based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
