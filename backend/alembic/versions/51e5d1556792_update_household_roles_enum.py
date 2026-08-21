"""Update household roles enum

Revision ID: 51e5d1556792
Revises: d9a1544cf4b8
Create Date: 2026-08-21 15:48:53.889480

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "51e5d1556792"
down_revision: Union[str, Sequence[str], None] = "d9a1544cf4b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace ADMIN with OWNER and add MANAGER."""

    op.execute(
        """
        ALTER TYPE household_role
        RENAME VALUE 'ADMIN' TO 'OWNER'
        """
    )

    op.execute(
        """
        ALTER TYPE household_role
        ADD VALUE 'MANAGER' AFTER 'OWNER'
        """
    )


def downgrade() -> None:
    """Restore the original ADMIN and MEMBER roles."""

    op.execute(
        """
        UPDATE household_users
        SET role = 'MEMBER'
        WHERE role = 'MANAGER'
        """
    )

    op.execute(
        """
        ALTER TYPE household_role
        RENAME TO household_role_old
        """
    )

    op.execute(
        """
        CREATE TYPE household_role AS ENUM (
            'ADMIN',
            'MEMBER'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE household_users
        ALTER COLUMN role TYPE household_role
        USING (
            CASE
                WHEN role::text = 'OWNER' THEN 'ADMIN'
                ELSE role::text
            END
        )::household_role
        """
    )

    op.execute(
        """
        DROP TYPE household_role_old
        """
    )