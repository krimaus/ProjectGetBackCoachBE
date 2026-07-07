from uuid import UUID

from fastapi import HTTPException
from starlette import status

from app.db_layer.orm_models.team import Team
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import and_, delete, select

from app.service_layer.pydantic_models import TeamItem
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.db_layer.orm_models.user import User
from src.app.db_layer.orm_models.user_role import UserRole
from src.app.service_layer.pydantic_models.team import AddMembersInput, ChangeNameInput, ChangeRankInput, CreateTeamInput, DeleteMembersInput


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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Users already on team: {sorted(already_members)}"
        )

    user_roles = [
        UserRole(user_id=user_id, team_id=team_id, role=UserRoleEnum.MEMBER)
        for user_id in existing_ids
    ]

    session.add_all(user_roles)
    await session.commit()

    return list(existing_ids)


async def delete_team_service(session: AsyncSession, team_id: UUID) -> None:
    stmt = delete(UserRole).where(
        UserRole.team_id == team_id
    )
    
    await session.execute(stmt)
    
    stmt = delete(Team).where(
        Team.id == team_id
    )
    
    await session.execute(stmt)
    await session.commit()
    
    
async def remove_team_members_service(session: AsyncSession, team_id: UUID, payload: DeleteMembersInput) -> None:
    stmt = delete(UserRole).where(
            and_(
                UserRole.team_id == team_id,
                UserRole.user_id.in_(set(payload.id_list))
            )
        )
    
    await session.execute(stmt)
    await session.commit()
    

async def rename_team_service(session: AsyncSession, team_id: UUID, payload: ChangeNameInput) -> Team:
    stmt = select(Team).where(Team.id == team_id)
    result = await session.execute(stmt)
    team = result.scalar_one_or_none()

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team not found: {team_id}"
        )

    team.name = payload.name
    await session.commit()
    await session.refresh(team)

    return team


async def change_member_rank_service(session: AsyncSession, team_id: UUID, user_id: UUID, payload: ChangeRankInput):
    stmt = select(UserRole).where(
            and_(
                UserRole.team_id == team_id,
                UserRole.user_id == user_id
            )
        )
    result = await session.execute(stmt)
    user_role = result.scalar_one_or_none()

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found in team."
        )

    user_role.role = payload.role
    await session.commit()
    await session.refresh(user_role)

    return user_role

async def change_team_ownership_service(session: AsyncSession, team_id: UUID, new_owner_id: UUID):
    stmt = select(UserRole).where(
            and_(
                UserRole.team_id == team_id,
                UserRole.role == UserRoleEnum.OWNER
            )
        )
    result = await session.execute(stmt)
    old_owner = result.scalars().one()
    old_owner.role = UserRoleEnum.COACH
    
    stmt = select(UserRole).where(
            and_(
                UserRole.team_id == team_id,
                UserRole.user_id == new_owner_id
            )
        )
    result = await session.execute(stmt)
    new_owner = result.scalar_one_or_none()
    
    if new_owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found in team."
        )
        
    new_owner.role = UserRoleEnum.OWNER
    await session.commit()
    await session.refresh(new_owner)
    return new_owner