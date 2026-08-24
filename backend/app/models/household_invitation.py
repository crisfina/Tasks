from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.household_role import HouseholdRole


class HouseholdInvitation(Base):
    __tablename__ = "household_invitations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id"),
        nullable=False,
    )

    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    accepted_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    role: Mapped[HouseholdRole] = mapped_column(
        Enum(HouseholdRole, name="household_role"),
        default=HouseholdRole.MEMBER,
        nullable=False,
    )

    code_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )