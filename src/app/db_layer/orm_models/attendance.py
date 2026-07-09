import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base


class AttendanceEntry(Base):
    __tablename__ = "attendance_entry"

    practice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("practice.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    planned_attendance: Mapped[bool | None] = mapped_column(default=None)
    actual_attendance: Mapped[bool | None] = mapped_column(default=None)