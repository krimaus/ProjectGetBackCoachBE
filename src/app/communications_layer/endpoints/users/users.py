from uuid import UUID

from fastapi import APIRouter
from starlette import status

from app.transaction_layer.services.users.common.listing import UsersListing
from app.transaction_layer.services.users.common.user_names_listing import UserNamesListing

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get(
    "/{team_id}/names",
    status_code=status.HTTP_200_OK,
)
async def get_users_names(team_id: UUID):
    return await UserNamesListing.service(team_id)

@users_router.get(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_users(team_id: UUID):
    return await UsersListing.service(team_id)