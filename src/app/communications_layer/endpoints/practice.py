import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_team_practices
from src.app.auth_util import user_dependency
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.service_layer.pydantic_models.practice import CreatePracticeInput, TeamPracticeListingItem
from src.app.service_layer.services.auth.service import check_user_role_in_team
from src.app.service_layer.services.practice.team_practice_listing.service import create_practice_service

practice_router = APIRouter(prefix="/practice", tags=["practice"])

@practice_router.get(
    "/practice/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_team_practice(
    team_id: UUID,
    user: user_dependency,
    time_from: dt.datetime | None = None,
    time_to: dt.datetime | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[TeamPracticeListingItem]:
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


@practice_router.post(
    "/practice/{team_id}",
    status_code=status.HTTP_201_CREATED
)
async def create_practice(
    team_id: UUID,
    payload: CreatePracticeInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in ("OWNER", "COACH"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
        
    return await create_practice_service(session, team_id, payload)