"""Add households and point scopes

Revision ID: 5580476509c9
Revises: 2c599a15d062
Create Date: 2026-08-06 15:17:32.999655

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "5580476509c9"
down_revision: Union[str, Sequence[str], None] = "2c599a15d062"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


point_scope = postgresql.ENUM(
    "HOUSEHOLD",
    "PERSONAL",
    name="point_scope",
    create_type=False,
)

household_role = postgresql.ENUM(
    "ADMIN",
    "MEMBER",
    name="household_role",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()

    point_scope.create(bind, checkfirst=True)
    household_role.create(bind, checkfirst=True)

    op.create_table(
        "households",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "household_users",
        sa.Column("household_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", household_role, nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            name="fk_household_users_household_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_household_users_user_id",
        ),
        sa.PrimaryKeyConstraint(
            "household_id",
            "user_id",
        ),
    )

    op.add_column(
        "categories",
        sa.Column(
            "household_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.drop_constraint(
        op.f("categories_name_key"),
        "categories",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_category_household_name",
        "categories",
        ["household_id", "name"],
    )

    op.create_foreign_key(
        "fk_categories_household_id",
        "categories",
        "households",
        ["household_id"],
        ["id"],
    )

    op.add_column(
        "events",
        sa.Column(
            "scope",
            point_scope,
            nullable=False,
        ),
    )

    op.add_column(
        "events",
        sa.Column(
            "household_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "events",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_events_household_id",
        "events",
        "households",
        ["household_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_events_user_id",
        "events",
        "users",
        ["user_id"],
        ["id"],
    )

    op.add_column(
        "point_transactions",
        sa.Column(
            "household_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "point_transactions",
        sa.Column(
            "scope",
            point_scope,
            nullable=False,
        ),
    )

    op.create_foreign_key(
        "fk_point_transactions_household_id",
        "point_transactions",
        "households",
        ["household_id"],
        ["id"],
    )

    op.add_column(
        "rooms",
        sa.Column(
            "household_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.drop_constraint(
        op.f("rooms_name_key"),
        "rooms",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_room_household_name",
        "rooms",
        ["household_id", "name"],
    )

    op.create_foreign_key(
        "fk_rooms_household_id",
        "rooms",
        "households",
        ["household_id"],
        ["id"],
    )

    op.add_column(
        "tasks",
        sa.Column(
            "household_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_tasks_household_id",
        "tasks",
        "households",
        ["household_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_tasks_household_id",
        "tasks",
        type_="foreignkey",
    )
    op.drop_column("tasks", "household_id")

    op.drop_constraint(
        "fk_rooms_household_id",
        "rooms",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_room_household_name",
        "rooms",
        type_="unique",
    )
    op.create_unique_constraint(
        op.f("rooms_name_key"),
        "rooms",
        ["name"],
    )
    op.drop_column("rooms", "household_id")

    op.drop_constraint(
        "fk_point_transactions_household_id",
        "point_transactions",
        type_="foreignkey",
    )
    op.drop_column("point_transactions", "scope")
    op.drop_column("point_transactions", "household_id")

    op.drop_constraint(
        "fk_events_user_id",
        "events",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_events_household_id",
        "events",
        type_="foreignkey",
    )
    op.drop_column("events", "user_id")
    op.drop_column("events", "household_id")
    op.drop_column("events", "scope")

    op.drop_constraint(
        "fk_categories_household_id",
        "categories",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_category_household_name",
        "categories",
        type_="unique",
    )
    op.create_unique_constraint(
        op.f("categories_name_key"),
        "categories",
        ["name"],
    )
    op.drop_column("categories", "household_id")

    op.drop_table("household_users")
    op.drop_table("households")

    bind = op.get_bind()

    household_role.drop(bind, checkfirst=True)
    point_scope.drop(bind, checkfirst=True)