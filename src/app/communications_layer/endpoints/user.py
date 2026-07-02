from fastapi import APIRouter, Depends
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_team_members_names_service, create_user_service
from src.app.service_layer.pydantic_models import UserItem
from src.app.service_layer.pydantic_models.user import CreateUserInput

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