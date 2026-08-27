from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .common import Base


class Invite(Base):
    __tablename__ = "invite"
    
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    
    player_consent: Mapped[bool | None] = mapped_column(nullable=True)
    team_consent: Mapped[bool | None] = mapped_column(nullable=True)