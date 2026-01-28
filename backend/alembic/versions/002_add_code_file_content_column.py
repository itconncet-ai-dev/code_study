"""Add content column to code_files table.

Stores code content in the database so that distributed Celery workers
can access it without needing shared filesystem access.

Revision ID: 002
Revises: 001
Create Date: 2026-01-26
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "code_files",
        sa.Column("content", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("code_files", "content")
