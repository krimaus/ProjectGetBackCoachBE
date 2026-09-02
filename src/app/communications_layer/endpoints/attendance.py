import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_attendance_grid
from app.auth_util import user_dependency
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.service_layer.services.auth.service import check_user_role_in_team

attendance_router = APIRouter(prefix="/attendance", tags=["attendance"])

@attendance_router.get(
    "/{team_id}/grid",
    status_code=status.HTTP_200_OK,
)
async def get_team_attendance_grid(
    team_id: UUID,
    user: user_dependency,
    time_from: dt.datetime | None = None,
    time_to: dt.datetime | None = None,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    if await check_user_role_in_team(session, user["id"], team_id) not in (UserRoleEnum.OWNER,UserRoleEnum.COACH,UserRoleEnum.MEMBER) :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
                
    if time_from is None:
        time_from = time_from = dt.datetime.now(dt.timezone.utc)
    if time_to is None:
        time_to = time_from + dt.timedelta(days=7)
        
    return await get_attendance_grid(session, team_id, time_from, time_to)