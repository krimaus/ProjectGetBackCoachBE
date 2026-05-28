from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_team_member_list

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get(
    "/{team_id}/names",
    status_code=status.HTTP_200_OK,
)
async def get_users_names(
    team_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await get_team_member_list(session, team_id)