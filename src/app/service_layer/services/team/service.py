from uuid import UUID

from fastapi import HTTPException

from app.db_layer.orm_models.team import Team
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.service_layer.pydantic_models import TeamItem
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.db_layer.orm_models.user import User
from src.app.db_layer.orm_models.user_role import UserRole
from src.app.service_layer.pydantic_models.team import AddMembersInput, CreateTeamInput


async def get_team_names(session: AsyncSession) -> list[TeamItem]:
    stmt = (
        select(Team.id, Team.name)
        .order_by(Team.name)
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [
        TeamItem(
            id=row.id,
            name=row.name
        )
        for row in rows
    ]
    
async def create_team_service(session: AsyncSession, user: dict, payload: CreateTeamInput) -> TeamItem:
    team = Team(
        name=payload.name
    )
    
    session.add(team)
    await session.commit()
    await session.refresh(team)
    
    user_role = UserRole(
        team_id=team.id,
        user_id=user['id'],
        role=UserRoleEnum.OWNER
    )
    
    session.add(user_role)
    await session.commit()
    
    return TeamItem(
        id=team.id,
        name=team.name
    )
    
async def add_team_members_service(session: AsyncSession, team_id: UUID, payload: AddMembersInput) -> list[UUID]:
    requested_ids = set(payload.id_list)

    stmt = select(User.id).where(User.id.in_(requested_ids))
    result = await session.execute(stmt)
    existing_ids = set(result.scalars().all())

    missing_ids = requested_ids - existing_ids
    if missing_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid user_ids: {sorted(missing_ids)}"
        )

    stmt = select(UserRole.user_id).where(
        UserRole.team_id == team_id,
        UserRole.user_id.in_(existing_ids)
    )
    result = await session.execute(stmt)
    already_members = set(result.scalars().all())

    if already_members:
        raise HTTPException(
            status_code=409,
            detail=f"Users already on team: {sorted(already_members)}"
        )

    user_roles = [
        UserRole(user_id=user_id, team_id=team_id, role=UserRoleEnum.MEMBER)
        for user_id in existing_ids
    ]

    session.add_all(user_roles)
    await session.commit()

    return list(existing_ids)
    