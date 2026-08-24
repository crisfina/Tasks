"""Allow personal categories

Revision ID: bbc5e41ddec7
Revises: 51e5d1556792
Create Date: 2026-08-24 09:01:56.159368

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bbc5e41ddec7"
down_revision: Union[str, Sequence[str], None] = "51e5d1556792"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow household and personal categories."""

    op.add_column(
        "categories",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.alter_column(
        "categories",
        "household_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.create_foreign_key(
        "fk_categories_user_id_users",
        "categories",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_unique_constraint(
        "uq_category_user_name",
        "categories",
        ["user_id", "name"],
    )

    op.create_check_constraint(
        "ck_category_single_owner",
        "categories",
        (
            "(household_id IS NOT NULL AND user_id IS NULL) "
            "OR "
            "(household_id IS NULL AND user_id IS NOT NULL)"
        ),
    )


def downgrade() -> None:
    """Restore categories belonging only to households."""

    op.drop_constraint(
        "ck_category_single_owner",
        "categories",
        type_="check",
    )

    op.execute(
        """
        UPDATE tasks
        SET category_id = NULL
        WHERE category_id IN (
            SELECT id
            FROM categories
            WHERE user_id IS NOT NULL
        )
        """
    )

    op.execute(
        """
        DELETE FROM categories
        WHERE user_id IS NOT NULL
        """
    )

    op.drop_constraint(
        "uq_category_user_name",
        "categories",
        type_="unique",
    )

    op.drop_constraint(
        "fk_categories_user_id_users",
        "categories",
        type_="foreignkey",
    )

    op.alter_column(
        "categories",
        "household_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column(
        "categories",
        "user_id",
    )