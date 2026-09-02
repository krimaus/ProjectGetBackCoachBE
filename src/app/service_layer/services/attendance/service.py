import datetime as dt
import uuid

from sqlalchemy import select

from app.db_layer.orm_models import Practice
from sqlalchemy.ext.asyncio import AsyncSession

from app.service_layer.pydantic_models import AttendanceItem, AttendanceListingItem
from app.db_layer.orm_models.attendance import AttendanceEntry


async def get_attendance_grid(
    session: AsyncSession,
    team_id: uuid.UUID,
    time_from: dt.datetime,
    time_to: dt.datetime,
) -> list[AttendanceListingItem]:
    stmt = (
        select(Practice.id, Practice.start_time, AttendanceEntry)
        .join(AttendanceEntry, AttendanceEntry.practice_id == Practice.id)
        .where(
            Practice.team_id == team_id,
            Practice.start_time >= time_from,
            Practice.start_time <= time_to,
        )
        .order_by(Practice.start_time)
    )
    result = await session.execute(stmt)
    rows = result.all()

    grouped: dict[uuid.UUID, AttendanceListingItem] = {}
    for practice_id, start_time, entry in rows:
        if practice_id not in grouped:
            grouped[practice_id] = AttendanceListingItem(date=start_time, attendance=[])
        grouped[practice_id].attendance.append(
            AttendanceItem(
                user_id=entry.user_id,
                real=entry.actual_attendance,
                planned=entry.planned_attendance,
            )
        )

    return list(grouped.values())