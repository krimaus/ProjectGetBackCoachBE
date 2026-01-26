import dataclasses
import uuid

from sqlalchemy import select

from app.db import get_session
from app.orm_models import Team


# @dataclasses.dataclass
# class OwnerItem:
#     id: uuid.UUID
#     username: str

@dataclasses.dataclass
class TeamsListingItem:
    id: uuid.UUID
    name: str
    # owner: OwnerItem

class TeamsNamesListing:

    @classmethod
    async def service(cls):
        # stmt = (
        #     select(Team.id, Team.name).order_by(Team.name)
        # )
        #
        # session = await get_session()
        # result = await session.execute(stmt)
        #
        # items = tuple(
        #     TeamsListingItem(**item)
        #     for item in result.mappings().fetchall()
        # )
        #
        # return items

        return [
            TeamsListingItem(
                id=uuid.uuid4(),
                name="Team Name 1"
            ),
            TeamsListingItem(
                id=uuid.uuid4(),
                name="Team Name 2"
            ),
            TeamsListingItem(
                id=uuid.uuid4(),
                name="Team Name 3"
            )
        ]