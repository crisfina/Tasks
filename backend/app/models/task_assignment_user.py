from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User

class TaskAssignmentUser(Base):
    __tablename__ = "task_assignment_users"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "user_id",
            name="uq_task_assignment_user",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    user: Mapped["User"] = relationship(
    back_populates="assigned_tasks"
    )

    task: Mapped["Task"] = relationship(
    back_populates="assigned_users"
    )

    order: Mapped[int | None] = mapped_column(Integer)