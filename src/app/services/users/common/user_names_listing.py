import dataclasses
import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.models import Team


@dataclasses.dataclass
class UserNamesListItem:
    id: UUID
    name: str

class UserNamesListing:

    @classmethod
    async def service(cls, team_id: UUID):
        # stmt = (
        #     select(Team).where(Team.id == team_id).options(joinedload(Team.owner, Team.coaches, Team.players))
        # )
        #
        # session = await get_session()
        # result = await session.execute(stmt)
        #
        # items = tuple(
        #     UserNamesListItem(**item)
        #     for item in result.mappings().fetchall()
        # )

        # return items

        return [
            UserNamesListItem(id=uuid.uuid4(), name="User Name 1"),
            UserNamesListItem(id=uuid.uuid4(), name="User Name 2"),
            UserNamesListItem(id=uuid.uuid4(), name="User Name 3"),
        ]