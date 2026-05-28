import uuid
import datetime as dt
from app.db_layer.orm_models import Practice
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.service_layer.pydantic_models import PracticeItem, TeamPracticeListingItem
    
# TODO: error handling 
async def get_team_practices(session: AsyncSession, team_id: uuid.UUID, time_from: dt.datetime, time_to: dt.datetime) -> list[TeamPracticeListingItem]:

    stmt = (
        select(Practice)
        .where(
            Practice.team_id == team_id,
            Practice.start_time >= time_from,
            Practice.end_time <= time_to,
        )
        .order_by(Practice.start_time)
    )

    result = await session.execute(stmt)
    practices = result.scalars().all()

    practice_by_date = defaultdict(list)
    for practice in practices:
        practice_by_date[practice.start_time.date()].append(practice)

    return [
        TeamPracticeListingItem(
            date=date,
            practice=[
                PracticeItem(
                    id=p.id,
                    start_time=p.start_time,
                    end_time=p.end_time,
                    description=p.description,
                )
                for p in daily_practices
            ],
        )
        for date, daily_practices in practice_by_date.items()
    ]