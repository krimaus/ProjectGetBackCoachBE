import datetime as dt
from uuid import UUID

from fastapi import HTTPException
from app.db_layer.orm_models import Practice
from collections import defaultdict
from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.service_layer.pydantic_models import BulkPracticeItem, TeamPracticeListingItem
from app.db_layer.orm_models.attendance import AttendanceEntry
from app.db_layer.orm_models.practice import PracticeSeries
from app.db_layer.orm_models.user_role import UserRole
from app.service_layer.pydantic_models.practice import CreatePracticeInput, CreateRecurringPracticeInput, MarkActualAttendanceInput, PracticeItem, UpdatePracticeInput
    
async def get_team_practice_service(session: AsyncSession, team_id: UUID, time_from: dt.datetime, time_to: dt.datetime) -> list[TeamPracticeListingItem]:

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
                BulkPracticeItem(
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
    
    
async def create_practice_service(
    session: AsyncSession, team_id: UUID, payload: CreatePracticeInput
) -> PracticeItem:
    practice = Practice(
        team_id=team_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
        description=payload.description,
    )
    session.add(practice)
    await session.flush()

    stmt = select(UserRole.user_id).where(UserRole.team_id == team_id)
    user_ids = (await session.execute(stmt)).scalars().all()

    session.add_all(
        AttendanceEntry(practice_id=practice.id, user_id=uid) for uid in user_ids
    )

    await session.commit()
    await session.refresh(practice)
    return PracticeItem(
        id=practice.id,
        team_id=practice.team_id,
        start_time=practice.start_time,
        end_time=practice.end_time,
        location=practice.location,
        description=practice.description,
        series_id=practice.series_id
    )


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


async def delete_practice_service(session: AsyncSession, team_id: UUID, practice_id: UUID) -> None:
    stmt = delete(Practice).where(
        Practice.id == practice_id,
        Practice.team_id == team_id,
    )
    result = await session.execute(stmt)

    if result.rowcount == 0:
        await session.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Practice not found")

    await session.commit()
    
    
async def mark_planned_attendance_service(
    session: AsyncSession, team_id: UUID, practice_id: UUID, user_id: UUID, attendance: bool
):
    stmt = select(Practice).where(
        and_(Practice.id == practice_id, Practice.team_id == team_id)
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if practice is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Practice not found")

    stmt = (
        update(AttendanceEntry)
        .where(
            AttendanceEntry.practice_id == practice_id,
            AttendanceEntry.user_id == user_id,
        )
        .values(planned_attendance=attendance)
    )
    result = await session.execute(stmt)

    if result.rowcount == 0:
        await session.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found in attendance list")

    await session.commit()

    entry_stmt = select(AttendanceEntry).where(
        AttendanceEntry.practice_id == practice_id,
        AttendanceEntry.user_id == user_id,
    )
    return (await session.execute(entry_stmt)).scalar_one()


async def mark_actual_attendance_service(
    session: AsyncSession,
    team_id: UUID,
    practice_id: UUID,
    payload: MarkActualAttendanceInput,
) -> list[AttendanceEntry]:
    practice_stmt = select(Practice.id).where(
        Practice.id == practice_id,
        Practice.team_id == team_id,
    )
    practice = (await session.execute(practice_stmt)).scalar_one_or_none()
    if practice is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Practice not found")
    
    if practice.end_date > dt.datetime.now(dt.timezone.utc):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Practice not finished")

    if not payload.entries:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No entries provided")

    params = [
        {
            "practice_id": practice_id,
            "user_id": entry.user_id,
            "actual_attendance": entry.actual_attendance,
        }
        for entry in payload.entries
    ]

    result = await session.execute(update(AttendanceEntry), params)

    if result.rowcount != len(params):
        await session.rollback()
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="One or more users are not part of this practice's attendance list",
        )

    await session.commit()

    entries_stmt = select(AttendanceEntry).where(AttendanceEntry.practice_id == practice_id)
    return (await session.execute(entries_stmt)).scalars().all()


async def create_recurring_practice_service(
    session: AsyncSession, team_id: UUID, payload: CreateRecurringPracticeInput
) -> list[PracticeItem]:
    series = PracticeSeries(
        team_id=team_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days_of_week=payload.days_of_week,
        start_time=payload.start_time,
        end_time=payload.end_time,
        location=payload.location,
        description=payload.description,
    )
    session.add(series)
    await session.flush()

    now = dt.datetime.now(dt.timezone.utc)
    practices: list[Practice] = []
    current = payload.start_date
    while current <= payload.end_date:
        if current.weekday() in payload.days_of_week:
            occurrence_start = dt.datetime.combine(
                current, payload.start_time, tzinfo=dt.timezone.utc
            )
            if occurrence_start > now:
                practices.append(
                    Practice(
                        team_id=team_id,
                        series_id=series.id,
                        start_time=occurrence_start,
                        end_time=dt.datetime.combine(
                            current, payload.end_time, tzinfo=dt.timezone.utc
                        ),
                        location=payload.location,
                        description=payload.description,
                    )
                )
        current += dt.timedelta(days=1)

    session.add_all(practices)
    await session.flush()
    
    stmt = select(UserRole.user_id).where(UserRole.team_id == team_id)
    user_ids = (await session.execute(stmt)).scalars().all()

    session.add_all(
        AttendanceEntry(practice_id=p.id, user_id=uid)
        for p in practices
        for uid in user_ids
    )

    await session.commit()
    for p in practices:
        await session.refresh(p)
    return [
        PracticeItem(
            id=p.id,
            team_id=p.team_id,
            start_time=p.start_time,
            end_time=p.end_time,
            location=p.location,
            description=p.description,
            series_id=p.series_id,
        )
        for p in practices
    ]



async def update_recurring_practice_service(
    session: AsyncSession, team_id: UUID, series_id: UUID, payload: CreateRecurringPracticeInput
) -> list[Practice]:
    stmt = select(PracticeSeries).where(PracticeSeries.id == series_id, PracticeSeries.team_id == team_id)
    
    result = await session.execute(stmt)
    series = result.scalar_one_or_none()
    
    if series is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Practice series not found for team",
        )

    now = dt.datetime.now(dt.timezone.utc)

    future_practices_stmt = select(Practice.id).where(
        Practice.series_id == series_id, Practice.start_time > now
    )
    result = await session.execute(future_practices_stmt)
    future_practice_ids = result.scalars().all()
    
    if future_practice_ids:
        await session.execute(
            delete(AttendanceEntry).where(AttendanceEntry.practice_id.in_(future_practice_ids))
        )
        await session.execute(
            delete(Practice).where(Practice.id.in_(future_practice_ids))
        )
        
    series.start_date = payload.start_date
    series.end_date = payload.end_date
    series.days_of_week = payload.days_of_week
    series.start_time = payload.start_time
    series.end_time = payload.end_time
    series.location = payload.location
    series.description = payload.description
    await session.flush()
    
    practices: list[Practice] = []
    current = payload.start_date
    while current <= payload.end_date:
        if current.weekday() in payload.days_of_week:
            occurrence_start = dt.datetime.combine(
                current, payload.start_time, tzinfo=dt.timezone.utc
            )
            if occurrence_start > now:
                practices.append(
                    Practice(
                        team_id=team_id,
                        series_id=series.id,
                        start_time=occurrence_start,
                        end_time=dt.datetime.combine(
                            current, payload.end_time, tzinfo=dt.timezone.utc
                        ),
                        location=payload.location,
                        description=payload.description,
                    )
                )
        current += dt.timedelta(days=1)

    session.add_all(practices)
    await session.flush()

    user_ids_stmt = select(UserRole.user_id).where(UserRole.team_id == team_id)
    result = await session.execute(user_ids_stmt)
    user_ids = result.scalars().all()

    session.add_all(
        AttendanceEntry(practice_id=p.id, user_id=uid)
        for p in practices
        for uid in user_ids
    )

    await session.commit()
    for p in practices:
        await session.refresh(p)
    return practices


async def delete_practice_series_service(
    session: AsyncSession, team_id: UUID, series_id: UUID
) -> None:
    stmt = select(PracticeSeries).where(
        PracticeSeries.id == series_id, PracticeSeries.team_id == team_id
    )
    series = (await session.execute(stmt)).scalar_one_or_none()
    if series is None:
        raise ValueError(f"Practice series not found for team")

    await session.delete(series)
    await session.commit()
    
    
async def get_practice_series_service(
    session: AsyncSession, team_id: UUID
) -> None:
    stmt = select(PracticeSeries).where(PracticeSeries.team_id == team_id)
    result = await session.execute(stmt)
    series = result.scalars().all()
    
    if series is None:
        raise ValueError(f"Practice series not found for team")

    return series