import uuid

from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base


class Attendance(Base):
    __tablename__ = "attendance"

    practice_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    
    attendance_list: Mapped[list[dict]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False
    )

    notes: Mapped[str]