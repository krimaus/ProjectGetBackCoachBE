from sqlalchemy.orm import Mapped, mapped_column

from .common import Base, IdBearer

class User(IdBearer, Base):
    __tablename__ = 'user'

    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
