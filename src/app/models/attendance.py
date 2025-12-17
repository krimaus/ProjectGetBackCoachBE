import typing
import uuid

from sqlalchemy.orm import Mapped, relationship, mapped_column

from .common import Base

if typing.TYPE_CHECKING:
    from app.models.practice import Practice
    from app.models.user import User


class Attendance(Base):
    __tablename__ = "attendance"

    practice_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    practice: Mapped["Practice"] = relationship()

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user: Mapped["User"] = relationship()

    planned_attendance: Mapped[bool]
    actual_attendance: Mapped[bool]

    notes: Mapped[str]
    # TODO: switch to holding a list of user ids for one practice id, 
    # when needed crossreference with current team members to avoid displaying non member users