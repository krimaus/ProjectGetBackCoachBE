import typing

from sqlalchemy.orm import Mapped

from .common import Base, IdBearer

if typing.TYPE_CHECKING:
    from app.db_layer.orm_models.user import User


class Team(IdBearer, Base):
    __tablename__ = "team"

    name: Mapped[str]