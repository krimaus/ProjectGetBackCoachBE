import datetime as dt
import uuid

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base, IdBearer


class Practice(IdBearer, Base):
    __tablename__ = "practice"

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE")
    )

    start_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))
    location: Mapped[str]
    notes: Mapped[str] = mapped_column(nullable=True)



