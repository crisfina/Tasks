"""Add household invitations

Revision ID: 345d1a6b98d2
Revises: 7a3001d33d34
Create Date: 2026-08-24 13:40:48.667923
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "345d1a6b98d2"
down_revision: Union[str, Sequence[str], None] = "7a3001d33d34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


household_role = postgresql.ENUM(
    "OWNER",
    "MANAGER",
    "MEMBER",
    name="household_role",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "household_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("accepted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("role", household_role, nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["accepted_by_user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_hash"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("household_invitations")