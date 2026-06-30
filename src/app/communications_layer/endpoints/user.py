from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_team_member_list, create_user_service
from src.app.service_layer.pydantic_models import UserItem
from src.app.service_layer.pydantic_models.user import CreateUserInput
from src.app.auth_util import user_dependency

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserItem,
)
async def create_user(
    payload: CreateUserInput,
    session: AsyncSession = Depends(get_session),
):
    return await create_user_service(session, payload)

@users_router.get(
    "/{team_id}/names",
    status_code=status.HTTP_200_OK,
)
async def get_users_names(
    team_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Aythentication failed'
        )
    return await get_team_member_list(session, team_id)