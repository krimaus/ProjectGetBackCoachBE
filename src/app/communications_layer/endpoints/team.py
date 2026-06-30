from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.pydantic_models.team import TeamItem
from app.service_layer.services import get_team_names
from src.app.auth_util import user_dependency
from src.app.service_layer.services.user.team_members_listing.service import get_team_member_list


teams_router = APIRouter(prefix="/teams", tags=["teams"])

@teams_router.get(
    "/names",
    status_code=status.HTTP_200_OK,
    response_model=list[TeamItem],
)
async def get_team_names_list(
    user: user_dependency,
    session: AsyncSession = Depends(get_session)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await get_team_names(session)

@teams_router.get(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK,
)
async def get_team_members_names(
    team_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await get_team_member_list(session, team_id)