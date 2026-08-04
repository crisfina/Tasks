"""Remove user role default

Revision ID: 2c599a15d062
Revises: ebb54e7dd70f
Create Date: 2026-08-04 10:00:58.666537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c599a15d062'
down_revision: Union[str, Sequence[str], None] = 'ebb54e7dd70f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
