import datetime as dt
import uuid

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from . import Team
from .common import Base, IdBearer


class Practice(IdBearer, Base):
    __tablename__ = "practice"

    team_id: Mapped[uuid.UUID]

    start_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))

    end_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP(timezone=True))

    location: Mapped[str]

    description: Mapped[str]



