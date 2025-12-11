import typing

from sqlalchemy.orm import Mapped, relationship

from .common import Base, IdBearer

if typing.TYPE_CHECKING:
    from app.models.user import User


class Team(IdBearer, Base):
    __tablename__ = "team"

    name: Mapped[str]

    owner: Mapped["User"] = relationship(back_populates="owned_teams")

    coaches: Mapped[list["User"]] = relationship(back_populates="coached_teams")

    players: Mapped[list["User"]] = relationship(back_populates="membership_teams")
