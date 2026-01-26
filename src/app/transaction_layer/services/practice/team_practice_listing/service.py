import dataclasses
import datetime as dt
import uuid

from sqlalchemy import select

from app.db import get_session
from app.db_layer.orm_models import Practice, Team


@dataclasses.dataclass
class PracticeItem:
    id: uuid.UUID
    start_time: dt.datetime
    end_time: dt.datetime
    description: str

@dataclasses.dataclass
class TeamPracticeListingItem:
    date: str
    practice: list[PracticeItem]

class TeamPracticeListing:

    @classmethod
    async def service(cls, team_id: uuid.UUID, time_from: dt.datetime | None, time_to: dt.datetime | None):

        # if time_from is None:
        #     time_from = dt.datetime.now()
        # if time_to is None:
        #     time_to = time_from + dt.timedelta(days=1)
        #
        # stmt = (
        #     select(
        #         Practice.id,
        #         Practice.start_time,
        #         Practice.end_time,
        #         Practice.description
        #     )
        #     .join(Team, Team.id == Practice.team.id)
        #     .filter(Team.id == team_id)
        #     .filter(Practice.start_time >= time_from)
        #     .filter(Practice.end_time <= time_to)
        #     .order_by(Practice.start_time)
        # )
        #
        # session = await get_session()
        # result = await session.execute(stmt)
        # practices = result.scalars().all()
        #
        # practice_by_date = {}
        # for practice in practices:
        #     practice_date = practice.start_time.date()
        #     if practice_date not in practice_by_date:
        #         practice_by_date[practice_date] = []
        #     practice_by_date[practice_date].append(practice)
        #
        # items = []
        # for date, practices_in_date in practice_by_date.items():
        #     practice_items = [
        #         PracticeItem(
        #             id=practice.id,
        #             start_time=practice.start_time,
        #             end_time=practice.end_time,
        #             description=practice.description
        #         )
        #         for practice in practices_in_date
        #     ]
        #
        #     items.append(
        #         TeamPracticeListingItem(
        #             date=date.strftime('%d-%m-%Y'),
        #             practice=practice_items
        #         )
        #     )
        #
        # return items

        return [
            TeamPracticeListingItem(
                date=str(dt.datetime.now().date()),
                practice=[
                    PracticeItem(
                        id=uuid.uuid4(),
                        start_time=dt.datetime.now(),
                        end_time=dt.datetime.now() + dt.timedelta(hours=2),
                        description="Sample description"
                    )
                ]
            ),
            TeamPracticeListingItem(
                date=str((dt.datetime.now()+dt.timedelta(days=1)).date()),
                practice=[
                    PracticeItem(
                        id=uuid.uuid4(),
                        start_time=dt.datetime.now() + dt.timedelta(days=1),
                        end_time=dt.datetime.now() + dt.timedelta(days=1, hours=2),
                        description="Sample description"
                    )
                ]
            )
        ]
