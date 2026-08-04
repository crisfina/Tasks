"""Remove user role default

Revision ID: ebb54e7dd70f
Revises: 3d9d34522b59
Create Date: 2026-08-04 10:00:53.792536
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ebb54e7dd70f"
down_revision: Union[str, Sequence[str], None] = "3d9d34522b59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "users",
        "role",
        server_default="USER",
    )