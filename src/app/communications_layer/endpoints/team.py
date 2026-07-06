from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.pydantic_models.team import AddMembersInput, CreateTeamInput, DeleteMembersInput, TeamItem
from app.service_layer.services import get_team_names
from src.app.auth_util import user_dependency
from src.app.service_layer.services.auth.service import check_user_role_in_team
from src.app.service_layer.services.team.service import add_team_members_service, create_team_service, delete_team_service, remove_team_members_service
from src.app.service_layer.services.user.team_members_listing.service import get_team_members_service


teams_router = APIRouter(prefix="/teams", tags=["teams"])

@teams_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TeamItem
)
async def create_team(
    payload: CreateTeamInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await create_team_service(session, user, payload)


@teams_router.post(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=list[UUID],
)
async def add_team_members(
    team_id: UUID,
    payload: AddMembersInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session)
):
    if user is None or await check_user_role_in_team(session, user['id'], team_id) == 'MEMBER':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await add_team_members_service(session, team_id, payload)        


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
async def get_team_members(
    team_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await get_team_members_service(session, team_id)


@teams_router.delete(
    "/{team_id}",
    status_code=status.HTTP_200_OK
)
async def delete_team(
    team_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None or await check_user_role_in_team(session, user['id'], team_id) != 'OWNER':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    
    await delete_team_service(session, team_id)
        

@teams_router.delete(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK
)
async def remove_team_members(
    team_id: UUID,
    payload: DeleteMembersInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None or await check_user_role_in_team(session, user['id'], team_id) == 'MEMBER':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    
    await remove_team_members_service(session, team_id, payload)