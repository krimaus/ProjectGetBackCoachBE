import datetime as dt
from uuid import UUID

from fastapi import APIRouter
from starlette import status

from service_layer.services.practice.team_practice_listing import get_team_practices

practice_router = APIRouter(prefix="/practice", tags=["practice"])

@practice_router.get(
    "/schedule/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_team_practice(
        team_id: UUID,
        time_from: dt.datetime | None = None,
        time_to: dt.datetime | None = None,
):
    if time_from is None:
        time_from = dt.datetime.now()
    if time_to is None:
        time_to = time_from + dt.timedelta(days=7)
        
    return await get_team_practices(team_id, time_from, time_to)