import datetime as dt
from uuid import UUID

from fastapi import APIRouter
from starlette import status

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
):
    if time_from is None:
        time_from = dt.datetime.now()
    if time_to is None:
        time_to = time_from + dt.timedelta(days=7)
        
    return await get_attendance_grid(team_id, time_from, time_to)