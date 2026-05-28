from fastapi import APIRouter, Depends
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.pydantic_models.team import TeamItem
from app.service_layer.services import get_team_names


teams_router = APIRouter(prefix="/teams", tags=["teams"])

@teams_router.get(
    "/names",
    status_code=status.HTTP_200_OK,
    response_model=list[TeamItem],
)
async def teams_listing(session: AsyncSession = Depends(get_session)):
    return await get_team_names(session)