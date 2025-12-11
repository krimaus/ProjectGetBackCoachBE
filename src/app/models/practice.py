import datetime as dt

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Team
from .common import Base, IdBearer


class Practice(IdBearer, Base):
    __tablename__ = "practice"

    team: Mapped["Team"] = relationship()

    start_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))

    end_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))

    location: Mapped[str]

    description: Mapped[str]



