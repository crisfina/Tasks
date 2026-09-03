from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "52d5bec89141"
down_revision: Union[str, Sequence[str], None] = "345d1a6b98d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "task_occurrences",
        sa.Column(
            "failed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "task_occurrences",
        sa.Column(
            "failed_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_task_occurrences_failed_by_user_id_users",
        "task_occurrences",
        "users",
        ["failed_by_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_task_occurrences_failed_by_user_id_users",
        "task_occurrences",
        type_="foreignkey",
    )
    op.drop_column(
        "task_occurrences",
        "failed_by_user_id",
    )
    op.drop_column(
        "task_occurrences",
        "failed_at",
    )