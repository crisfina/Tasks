"""Add household owner and manager roles

Revision ID: d9a1544cf4b8
Revises: 4cd5e01433d2
Create Date: 2026-08-21 15:28:10.907096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9a1544cf4b8'
down_revision: Union[str, Sequence[str], None] = '4cd5e01433d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
