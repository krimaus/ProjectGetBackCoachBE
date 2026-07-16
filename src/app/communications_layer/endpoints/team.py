from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.pydantic_models.team import AddMembersInput, ChangeNameInput, ChangeRankInput, CreateTeamInput, DeleteMembersInput, TeamItem
from app.service_layer.services import get_team_names
from src.app.auth_util import user_dependency
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.service_layer.services.auth.service import check_user_role_in_team
from src.app.service_layer.services.team.service import add_team_members_service, change_member_rank_service, change_team_ownership_service, rename_team_service, create_team_service, delete_team_service, remove_team_members_service, search_team_by_name_service
from src.app.service_layer.services.user.service import get_team_members_service


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


@teams_router.patch(
    "/{team_id}/members/add",
    status_code=status.HTTP_200_OK,
    response_model=list[UUID],
)
async def add_team_members(
    team_id: UUID,
    payload: AddMembersInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER, UserRoleEnum.COACH):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
    return await add_team_members_service(session, team_id, payload)


@teams_router.patch(
    "/{team_id}",
    status_code=status.HTTP_200_OK
)
async def rename_team(
    team_id: UUID,
    payload: ChangeNameInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
    
    return await rename_team_service(session, team_id, payload)


@teams_router.patch(
    "/{team_id}/{user_id}/rank",
    status_code=status.HTTP_200_OK
)
async def change_member_rank(
    team_id: UUID,
    user_id: UUID,
    payload: ChangeRankInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
        
    return await change_member_rank_service(session, team_id, user_id, payload)


@teams_router.patch(
    "/{team_id}/{user_id}/owner",
    status_code=status.HTTP_200_OK
)
async def change_team_ownership(
    team_id: UUID,
    user_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
    return await change_team_ownership_service(session, team_id, user_id)


@teams_router.patch(
    "/{team_id}/members/remove",
    status_code=status.HTTP_200_OK
)
async def remove_team_members(
    team_id: UUID,
    payload: DeleteMembersInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER, UserRoleEnum.COACH):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
    
    await remove_team_members_service(session, team_id, payload)


@teams_router.get(
    "/search/{name_query}",
    status_code=status.HTTP_200_OK
)
async def search_team_by_name(
    name_query: Annotated[str, Path(min_length=2, max_length=100)],
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> list[TeamItem]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await search_team_by_name_service(session, name_query)


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
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Insufficient permissions'
        )
    
    await delete_team_service(session, team_id)