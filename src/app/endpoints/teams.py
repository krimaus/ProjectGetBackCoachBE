from fastapi import APIRouter
from starlette import status

from app.services.teams.listing.service import TeamsNamesListing

teams_router = APIRouter(prefix="/teams", tags=["teams"])

@teams_router.get(
    "/names",
    status_code=status.HTTP_200_OK,
)
async def teams_listing():
    return await TeamsNamesListing.service()