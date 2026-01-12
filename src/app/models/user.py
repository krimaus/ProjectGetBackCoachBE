import typing

from sqlalchemy.orm import Mapped, relationship

from .common import Base, IdBearer

if typing.TYPE_CHECKING:
    from app.models.team import Team

class User(IdBearer, Base):
    __tablename__ = 'user'

    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str]
