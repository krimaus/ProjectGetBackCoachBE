import typing

from sqlalchemy.orm import Mapped

from .common import Base, IdBearer

class User(IdBearer, Base):
    __tablename__ = 'user'

    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str]
