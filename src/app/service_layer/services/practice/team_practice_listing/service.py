import datetime as dt
from uuid import UUID
from app.db_layer.orm_models import Practice
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.service_layer.pydantic_models import PracticeItem, TeamPracticeListingItem
from src.app.db_layer.orm_models.attendance import Attendance
from src.app.db_layer.orm_models.user_role import UserRole
from src.app.service_layer.pydantic_models.practice import CreatePracticeInput, UpdatePracticeInput
    
# TODO: error handling 
async def get_team_practices(session: AsyncSession, team_id: UUID, time_from: dt.datetime, time_to: dt.datetime) -> list[TeamPracticeListingItem]:

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
    
    
async def create_practice_service(session: AsyncSession, team_id: UUID, payload: CreatePracticeInput):
    practice = Practice(
        team_id=team_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
        description=payload.description,
    )
    
    session.add(practice)
    await session.flush()
    
    stmt = select(UserRole).where(
            UserRole.team_id==team_id
    )
    
    result = await session.execute(stmt)
    members = result.scalars().all()
    
    attendance = Attendance(
        practice_id=practice.id,
        attendance_list=[
            {
                "user_id": str(member.user_id),
                "planned_attendance": None,
                "actual_attendance": None,
            } for member in members
        ],
        notes=None
    )
    
    session.add(attendance)
    await session.commit()
    await session.refresh(practice)
    
    return practice


async def update_practice_service(session: AsyncSession, practice_id: UUID, payload: UpdatePracticeInput):
    stmt = select(Practice).where(Practice.id == practice_id)
    
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()
    
    practice.start_time = payload.start_time
    practice.end_time = payload.end_time
    practice.location = payload.location
    practice.description = payload.description
    
    await session.commit()
    await session.refresh(practice)

    return practice
    
    