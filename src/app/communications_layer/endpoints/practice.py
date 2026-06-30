import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_team_practices
from src.app.auth_util import user_dependency

practice_router = APIRouter(prefix="/practice", tags=["practice"])

@practice_router.get(
    "/schedule/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_team_practice(
    team_id: UUID,
    user: user_dependency,
    time_from: dt.datetime | None = None,
    time_to: dt.datetime | None = None,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if time_from is None:
        time_from = dt.datetime.now(dt.timezone.utc)
    if time_to is None:
        time_to = time_from + dt.timedelta(days=7)
        
    return await get_team_practices(session, team_id, time_from, time_to)