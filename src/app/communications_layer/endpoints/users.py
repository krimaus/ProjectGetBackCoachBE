from uuid import UUID

from fastapi import APIRouter
from starlette import status

from app.transaction_layer.services.user.user_list import get_team_member_list


users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get(
    "/{team_id}/names",
    status_code=status.HTTP_200_OK,
)
async def get_users_names(team_id: UUID):
    return await get_team_member_list(team_id)