"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Migration Description:
    ${message}

AI Code Learning Platform - Database Migration
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Revision identifiers, used by Alembic
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """
    Upgrade database schema.

    Apply forward migration changes. This function should:
    - Create new tables
    - Add new columns
    - Create new indexes
    - Apply any data migrations

    Operations are applied in order and should be reversible.
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """
    Downgrade database schema.

    Revert migration changes. This function should:
    - Drop tables created in upgrade
    - Remove columns added in upgrade
    - Drop indexes created in upgrade
    - Revert any data migrations

    Operations should exactly reverse the upgrade function.
    """
    ${downgrades if downgrades else "pass"}
