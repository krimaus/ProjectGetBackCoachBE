from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import create_user_service
from src.app.service_layer.pydantic_models import UserItem
from src.app.service_layer.pydantic_models.user import CreateUserInput, UpdateUserInput
from src.app.auth_util import user_dependency
from src.app.service_layer.pydantic_models.user_role import UserRoleItem
from src.app.service_layer.services.user.service import delete_user_service, get_user_by_name_service, get_user_roles_service, get_user_by_id_service, search_user_by_name_service, update_user_service

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get(
    "/current",
    status_code=status.HTTP_200_OK
)
async def get_current_user(
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> UserItem:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await get_user_by_id_service(session, user['id'])


@users_router.get(
    "/{name}",
    status_code=status.HTTP_200_OK
)
async def get_user_by_name(
    name: str,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> UserItem:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await get_user_by_name_service(session, name)


@users_router.get(
    "/search/{name_query}",
    status_code=status.HTTP_200_OK
)
async def search_user_by_name(
    name_query: Annotated[str, Path(min_length=2, max_length=100)],
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> list[UserItem]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    return await search_user_by_name_service(session, name_query)


@users_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK
)
async def get_user_by_id(
    user_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> UserItem:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
        
    return await get_user_by_id_service(session, user_id)


@users_router.get(
    "/{user_id}/roles",
    status_code=status.HTTP_200_OK
)
async def get_user_roles(
    user_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> list[UserRoleItem]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
        
    return await get_user_roles_service(session, user_id)


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


@users_router.patch(
    "/",
    status_code=status.HTTP_200_OK
)
async def update_user(
    payload: UpdateUserInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> UserItem:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
        
    return await update_user_service(session, user['id'], payload)


@users_router.delete(
    "/",
    status_code=status.HTTP_200_OK
)
async def delete_user(
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    
    await delete_user_service(session, user['id'])