import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.service_layer.services import get_team_practice_service
from app.auth_util import user_dependency
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.service_layer.pydantic_models.practice import CreatePracticeInput, CreateRecurringPracticeInput, MarkActualAttendanceInput, PracticeItem, TeamPracticeListingItem, UpdatePracticeInput, UpdateRecurringPracticeInput
from app.service_layer.services.auth.service import check_user_role_in_team
from app.service_layer.services.practice.service import create_practice_service, create_recurring_practice_service, delete_practice_series_service, delete_practice_service, get_practice_series_service, mark_actual_attendance_service, mark_planned_attendance_service, update_practice_service, update_recurring_practice_service

practice_router = APIRouter(prefix="/practice", tags=["practice"])

@practice_router.get(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_team_practice(
    team_id: UUID,
    user: user_dependency,
    time_from: dt.datetime | None = None,
    time_to: dt.datetime | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[TeamPracticeListingItem]:
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
        time_from = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)
    if time_to is None:
        time_to = time_from + dt.timedelta(days=7)
        
    return await get_team_practice_service(session, team_id, time_from, time_to)


@practice_router.get(
    "/{team_id}/recurring",
    status_code=status.HTTP_201_CREATED,
)
async def get_recurring_practice_for_team(
    team_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    if await check_user_role_in_team(session, user["id"], team_id) not in (UserRoleEnum.OWNER,UserRoleEnum.COACH) :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return await get_practice_series_service(session, team_id)


@practice_router.post(
    "/{team_id}",
    status_code=status.HTTP_201_CREATED
)
async def create_practice(
    team_id: UUID,
    payload: CreatePracticeInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> PracticeItem:
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
        
    return await create_practice_service(session, team_id, payload)


@practice_router.post(
    "/{team_id}/recurring",
    status_code=status.HTTP_201_CREATED,
)
async def create_recurring_practice(
    team_id: UUID,
    payload: CreateRecurringPracticeInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> list[PracticeItem]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    if await check_user_role_in_team(session, user["id"], team_id) not in (UserRoleEnum.OWNER, UserRoleEnum.COACH):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return await create_recurring_practice_service(session, team_id, payload)


@practice_router.put(
    "/{team_id}/recurring/{series_id}",
    status_code=status.HTTP_201_CREATED,
)
async def update_recurring_practice(
    team_id: UUID,
    series_id: UUID,
    payload: UpdateRecurringPracticeInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    if await check_user_role_in_team(session, user["id"], team_id) not in (UserRoleEnum.OWNER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return await update_recurring_practice_service(session, team_id, series_id, payload)


@practice_router.put(
    "/{team_id}/{practice_id}",
    status_code=status.HTTP_200_OK
)
async def update_practice(
    team_id: UUID,
    practice_id: UUID,
    payload: UpdatePracticeInput,
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
    
    return await update_practice_service(session, practice_id, payload)


@practice_router.patch(
    "/{team_id}/{practice_id}/attendance/planned",
    status_code=status.HTTP_200_OK
)
async def mark_planned_attendance(
    team_id: UUID,
    practice_id: UUID,
    attendance: bool,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed'
        )
    
    return await mark_planned_attendance_service(session, team_id, practice_id, user['id'], attendance)


@practice_router.patch(
    "/{team_id}/{practice_id}/attendance/actual",
    status_code=status.HTTP_200_OK,
)
async def mark_actual_attendance(
    team_id: UUID,
    practice_id: UUID,
    payload: MarkActualAttendanceInput,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')

    if await check_user_role_in_team(session, user['id'], team_id) not in (UserRoleEnum.OWNER, UserRoleEnum.COACH):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')

    return await mark_actual_attendance_service(session, team_id, practice_id, payload)


@practice_router.delete(
    "/{team_id}/{practice_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_practice(
    team_id: UUID,
    practice_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
) -> None:
    
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
    
    await delete_practice_service(session, team_id, practice_id)
    

@practice_router.delete(
    "/{team_id}/recurring/{series_id}",
    status_code=status.HTTP_201_CREATED,
)
async def delete_recurring_practice(
    team_id: UUID,
    series_id: UUID,
    user: user_dependency,
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    if await check_user_role_in_team(session, user["id"], team_id) not in (UserRoleEnum.OWNER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return await delete_practice_series_service(session, team_id, series_id)