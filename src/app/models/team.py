import typing

from sqlalchemy.orm import Mapped, relationship

from .common import Base, IdBearer

if typing.TYPE_CHECKING:
    from app.models.user import User


class Team(IdBearer, Base):
    __tablename__ = "team"

    name: Mapped[str]