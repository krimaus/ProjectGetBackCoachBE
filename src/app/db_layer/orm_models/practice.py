import datetime as dt
import uuid

from sqlalchemy import ARRAY, TIME, TIMESTAMP, ForeignKey, Integer
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
    description: Mapped[str | None] = mapped_column(nullable=True)
    series_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("practice_series.id"), nullable=True
    )


class PracticeSeries(IdBearer, Base):
    __tablename__ = "practice_series"

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE")
    )
    start_date: Mapped[dt.date]
    end_date: Mapped[dt.date]
    days_of_week: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    start_time: Mapped[dt.time] = mapped_column(TIME(timezone=True))
    end_time: Mapped[dt.time] = mapped_column(TIME(timezone=True))
    location: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)