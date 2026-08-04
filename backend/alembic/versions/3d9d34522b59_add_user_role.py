"""Add user role

Revision ID: 3d9d34522b59
Revises: 58fc4c941563
Create Date: 2026-08-04 09:28:29.949712

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d9d34522b59"
down_revision: Union[str, Sequence[str], None] = "58fc4c941563"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    user_role = sa.Enum("ADMIN", "USER", name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="USER",
        ),
    )



def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("users", "role")

    user_role = sa.Enum("ADMIN", "USER", name="user_role")
    user_role.drop(op.get_bind(), checkfirst=True)