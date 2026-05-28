import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from service_layer.services.attendance.attendance_grid.service import get_attendance_grid

attendance_router = APIRouter(prefix="/attendance", tags=["attendance"])

@attendance_router.get(
    "/{team_id}/grid",
    status_code=status.HTTP_200_OK,
)
async def get_team_attendance_grid(
    team_id: UUID,
    time_from: dt.datetime | None = None,
    time_to: dt.datetime | None = None,
    session: AsyncSession = Depends(get_session),
):
    if time_from is None:
        time_from = time_from = dt.datetime.now(dt.timezone.utc)
    if time_to is None:
        time_to = time_from + dt.timedelta(days=7)
        
    return await get_attendance_grid(session, team_id, time_from, time_to)