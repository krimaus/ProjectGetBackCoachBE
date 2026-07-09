import uuid

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base


class Attendance(Base):
    __tablename__ = "attendance"

    practice_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    notes: Mapped[str | None]
    
    
class AttendanceEntry(Base):
    __tablename__ = "attendance_entry"

    practice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attendance.practice_id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )

    planned_attendance: Mapped[bool | None] = mapped_column(default=None)
    actual_attendance: Mapped[bool | None] = mapped_column(default=None)