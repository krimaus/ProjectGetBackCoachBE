from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from starlette import status

from app.services.practice.practice_attendance_listing.service import TeamAttendanceListing
from app.services.practice.team_practice_listing.service import TeamPracticeListing

practice_router = APIRouter(prefix="/practice", tags=["practice"])

@practice_router.get(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_team_practice(
        team_id: UUID,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
):
    return await TeamPracticeListing.service(team_id, time_from, time_to)

@practice_router.get(
    "/{team_id}/attendance",
    status_code=status.HTTP_200_OK,
)
async def get_team_practice_attendance(team_id: UUID):
    return await TeamAttendanceListing.service(team_id)