import typing
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum

from .common import Base
from .enums import UserRoleEnum

if typing.TYPE_CHECKING:
    from app.models.team import Team


class UserRole(Base):
    __tablename__ = "user_role"

    team_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum, name="user_role_enum"),
        nullable=False,
    )

