from sqlalchemy.orm import Mapped

from .common import Base, IdBearer


class Team(IdBearer, Base):
    __tablename__ = "team"

    name: Mapped[str]