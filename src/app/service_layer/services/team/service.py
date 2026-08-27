from uuid import UUID

from fastapi import HTTPException
from starlette import status

from app.db_layer.orm_models.team import Team
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import and_, delete, or_, select

from app.service_layer.pydantic_models import TeamItem
from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.db_layer.orm_models.invite import Invite
from src.app.db_layer.orm_models.user import User
from src.app.db_layer.orm_models.user_role import UserRole
from src.app.service_layer.pydantic_models.enums.invite_status import InviteStatus
from src.app.service_layer.pydantic_models.enums.membership_application import MembershipApplicationDecisionEnum
from src.app.service_layer.pydantic_models.team import DeleteInviteInput, InviteMembersInput, ChangeNameInput, ChangeRankInput, CreateTeamInput, DeleteMembersInput


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
    
async def invite_team_members_service(session: AsyncSession, team_id: UUID, payload: InviteMembersInput) -> list[UUID]:
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

    stmt = select(Invite).where(
        Invite.team_id == team_id,
        Invite.user_id.in_(payload.id_list),
        or_(
            Invite.player_consent == None,
            Invite.team_consent == None
        )
    )
    already_invited = result.scalars().all()
    
    if already_invited:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Players already invited or requesting join {[invite.user_id for invite in already_invited]}"
        )
        
    session.add_all(
        Invite(team_id=team_id, user_id=user_id, player_consent=None, team_consent=True)
        for user_id in existing_ids
    )
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
    
    
async def remove_team_members_service(
    session: AsyncSession, team_id: UUID, payload: DeleteMembersInput
) -> None:
    target_ids = set(payload.id_list)

    owner_stmt = select(UserRole.user_id).where(
        UserRole.team_id == team_id,
        UserRole.role == UserRoleEnum.OWNER,
    )
    owner_id = (await session.execute(owner_stmt)).scalar_one_or_none()

    if owner_id is not None and owner_id in target_ids:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Team owner must transfer ownership before being removed",
        )

    stmt = delete(UserRole).where(
        UserRole.team_id == team_id,
        UserRole.user_id.in_(target_ids)
    )
    result = await session.execute(stmt)

    if result.rowcount != len(target_ids):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="One or more users are not members of this team",
        )

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


async def search_team_by_name_service(session: AsyncSession, name_query: str) -> list[TeamItem]:
    stmt = (
    select(Team)
    .where(
        Team.name.ilike(f"{name_query}%")
    )
    .order_by(Team.name, Team.id)
)
    result = await session.execute(stmt)
    teams = result.scalars().all()
    
    return [
        TeamItem(
            id=team.id,
            name=team.name
        ) for team in teams
    ]
    
    
async def resolve_join_request_service(session: AsyncSession, team_id: UUID, user_id: UUID, decision: MembershipApplicationDecisionEnum):
    stmt = select(UserRole.user_id).where(
        UserRole.team_id == team_id,
        UserRole.user_id == user_id,
    )
    result = await session.execute(stmt)
    already_member = result.scalar_one_or_none()

    if already_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already on team"
        )
        
    stmt = select(Invite).where(
        Invite.team_id == team_id,
        Invite.user_id == user_id,
        Invite.team_consent == None
    )
    result = await session.execute(stmt)
    invite = result.scalar_one_or_none()
    
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invite not found"
        )
        
    if decision == MembershipApplicationDecisionEnum.ACCEPT:
        invite.team_consent = True
        
        new_role = UserRole(
                user_id=user_id,
                team_id=team_id,
                role=UserRoleEnum.MEMBER
            )
            
        session.add(new_role)
        await session.commit()
        
        return new_role
    else:
        invite.team_consent = False
        await session.commit()
        return None
    
    
async def delete_invite_service(session: AsyncSession, team_id: UUID, payload: DeleteInviteInput):
    stmt = select(Invite).where(
        Invite.team_id == team_id,
        Invite.user_id.in_(payload.id_list),
    )
    result = await session.execute(stmt)
    invites = result.scalars().all()
    
    if invites is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invite not found"
        )
        
    consent = [invite.team_consent for invite in invites]
        
    if None in consent:
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invite must be resolved or created by team"
        )
        
    stmt = delete(Invite).where(
        Invite.team_id == team_id,
        Invite.user_id.in_(payload.id_list),
    )
    await session.execute(stmt)
    
    
async def get_team_invites_service(session: AsyncSession, team_id: UUID, invite_status: InviteStatus):
    stmt = select(Invite).where(
        Invite.team_id == team_id,
    )
    
    if invite_status == InviteStatus.ACTIVE:
        stmt = stmt.where(
            or_(
                Invite.player_consent is None,
                Invite.team_consent is None
            )
        )
    elif invite_status== InviteStatus.RESOLVED:
        stmt = stmt.where(
            Invite.player_consent is not None,
            Invite.team_consent is not None
        )
    
    result = await session.execute(stmt)
    invites = result.scalars().all()
    
    if invites is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invite not found"
        )
        
    return invites