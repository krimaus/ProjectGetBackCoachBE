import dataclasses
import datetime as dt
import enum
import uuid


class UserStatusEnum(enum.StrEnum):
    OWNER = "owner"
    COACH = "coach"
    MEMBER = "member"

@dataclasses.dataclass
class UsersListingItem:
    id: uuid.UUID
    name: str
    birthday: dt.date
    status: UserStatusEnum


class UsersListing:

    @classmethod
    async def service(cls, team_id: uuid.UUID):

        return [
            UsersListingItem(
                id=uuid.uuid4(),
                name="User Name 1",
                birthday=(dt.datetime.today() - dt.timedelta(days=4100)).date(),
                status=UserStatusEnum.OWNER,
            ),
            UsersListingItem(
                id=uuid.uuid4(),
                name="User Name 2",
                birthday=(dt.datetime.today() - dt.timedelta(days=4200)).date(),
                status=UserStatusEnum.COACH,
            ),
            UsersListingItem(
                id=uuid.uuid4(),
                name="User Name 3",
                birthday=(dt.datetime.today() - dt.timedelta(days=4300)).date(),
                status=UserStatusEnum.MEMBER,
            ),
        ]