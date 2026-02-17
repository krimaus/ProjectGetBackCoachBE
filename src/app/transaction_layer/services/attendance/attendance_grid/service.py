from collections import defaultdict
import datetime as dt
import uuid

from sqlalchemy import select

from app.db import get_session
from app.db_layer.orm_models import Practice, Attendance
from pydantic_models.attendance import AttendanceItem, AttendanceListingItem

# TODO: error handling 
async def get_attendance_grid(team_id: uuid.UUID, time_from: dt.datetime, time_to: dt.datetime):
    async with await get_session() as session:
        stmt = (
            select(Attendance, Practice.start_time)
            .join(Practice, Attendance.practice_id == Practice.id)
            .where(
                Practice.team_id == team_id,
                Practice.start_time >= time_from,
                Practice.end_time <= time_to,
            )
            .order_by(Practice.start_time)
        )

        result = await session.execute(stmt)
        rows = result.all()

    return [
        AttendanceListingItem(
            date=start_time,
            attendance=[
                AttendanceItem(
                    user_id=entry.user_id,
                    real=entry.real,
                    planned=entry.planned,
                )
                for entry in attendance.attendance_list
            ],
        )
        for attendance, start_time in rows
    ]
