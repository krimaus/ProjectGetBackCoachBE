import uuid

from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.service_layer.pydantic_models import UserItem
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.db_layer.orm_models.invite import Invite
from app.service_layer.pydantic_models.enums.invite_status import InviteStatus
from app.service_layer.pydantic_models.enums.membership_application import MembershipApplicationDecisionEnum
from app.service_layer.pydantic_models.user import CreateUserInput, UpdateUserInput
from app.auth_util import password_hash
from app.service_layer.pydantic_models.user_role import UserRoleItem


async def create_user_service(session: AsyncSession, payload: CreateUserInput) -> UserItem:
    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        username=payload.username,
        hashed_password=password_hash.hash(payload.password),
    )

    session.add(user)

    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    return UserItem(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        username=user.username,
    )


async def get_team_members_service(session: AsyncSession, team_id: uuid.UUID) -> list[UserItem]:
  
    stmt = (
        select(User)
        .join(UserRole, User.id == UserRole.user_id)
        .where(
            UserRole.team_id == team_id
        )
        .order_by(User.last_name)
    )
    
    result = await session.execute(stmt)
    members = result.scalars().all()
        
    return [
            UserItem(
                id=m.id,
                first_name=m.first_name,
                last_name=m.last_name,
                full_name=m.full_name,
                username=m.username
            )
            for m in members
        ]
    

async def delete_user_service(session: AsyncSession, user_id: uuid.UUID) -> None:
    stmt = select(UserRole.team_id).where(
        UserRole.user_id == user_id,
        UserRole.role == UserRoleEnum.OWNER,
    )
    result = await session.execute(stmt)
    owned_team_ids = result.scalars().all()

    if owned_team_ids:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"User owns {len(owned_team_ids)} team(s); transfer ownership before deleting",
        )
        
    stmt = delete(User).where(User.id == user_id)
    
    await session.execute(stmt)
    await session.commit()
    
    
async def update_user_service(session: AsyncSession, user_id: uuid.UUID, payload: UpdateUserInput) -> UserItem:
    stmt = select(User).where(User.id == user_id)
    
    result = await session.execute(stmt)
    user = result.scalars().one()
    
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    user.username = payload.username
    
    await session.commit()
    
    return UserItem(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        username=user.username
    )
    
    
async def get_user_by_id_service(session: AsyncSession, user_id: uuid.UUID) -> UserItem:
    stmt = select(User).where(User.id == user_id)
    
    result = await session.execute(stmt)
    user = result.scalars().one()
    
    return UserItem(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        username=user.username
    )
    
    
async def get_user_roles_service(session: AsyncSession, user_id: uuid.UUID) -> UserRoleItem:
    stmt = select(UserRole).where(UserRole.user_id == user_id)
    
    result = await session.execute(stmt)
    user_roles = result.scalars().all()
    
    return [
        UserRoleItem(
            team_id=role.team_id,
            user_id=role.user_id,
            role=role.role
        ) for role in user_roles
    ]
    
    
async def get_user_by_name_service(session: AsyncSession, name: str) -> UserItem:
    stmt = select(User).where(User.full_name == name)
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )
        
    return UserItem(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        username=user.username
    )
    
    
async def search_user_by_name_service(session: AsyncSession, name_query: str) -> list[UserItem]:
    stmt = (
    select(User)
    .where(
        or_(
            User.first_name.ilike(f"{name_query}%"),
            User.last_name.ilike(f"{name_query}%"),
        )
    )
    .order_by(User.last_name, User.first_name, User.id)
)
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    return [
        UserItem(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            username=user.username
        ) for user in users
    ]
    
    
async def request_join_team_service(session: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID):
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
        or_(
            Invite.player_consent == None,
            Invite.team_consent == None
        )
    )
    result = await session.execute(stmt)
    already_invited = result.scalar_one_or_none()
    
    if already_invited:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Player already invited or requesting join"
        )
        
    session.add_all(
        Invite(team_id=team_id, user_id=user_id, player_consent=True, team_consent=None)
    )
    await session.commit()
    
    
async def resolve_team_invite_service(session: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID, decision: MembershipApplicationDecisionEnum):
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
        Invite.player_consent == None
    )
    result = await session.execute(stmt)
    invite = result.scalar_one_or_none()
    
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invite not found"
        )
        
    if decision == MembershipApplicationDecisionEnum.ACCEPT:
        invite.player_consent = True
            
        new_role = UserRole(
                user_id=user_id,
                team_id=team_id,
                role=UserRoleEnum.MEMBER
            )
            
        session.add(new_role)
        await session.commit()
        
        return new_role
    else:
        invite.player_consent = False
        await session.commit()
        return None
    
    
async def delete_join_request_service(session: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID):
    stmt = select(Invite).where(
        Invite.team_id == team_id,
        Invite.user_id == user_id,
    )
    result = await session.execute(stmt)
    invite = result.scalar_one_or_none()
    
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invite not found"
        )
    if invite.player_consent is None:
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invite must be resolved or created by user"
        )
        
    stmt = delete(Invite).where(
        Invite.team_id == team_id,
        Invite.user_id == user_id,
    )
    await session.execute(stmt)
        
        
async def get_user_invites_service(session: AsyncSession, user_id: uuid.UUID, invite_status: InviteStatus):
    stmt = select(Invite).where(
        Invite.user_id == user_id,
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


async def leave_team_service(session: AsyncSession, team_id: uuid.UUID, user_id: uuid.UUID):
    owner_stmt = select(UserRole.user_id).where(
        UserRole.team_id == team_id,
        UserRole.role == UserRoleEnum.OWNER,
    )
    owner_id = (await session.execute(owner_stmt)).scalar_one_or_none()

    if owner_id is not None and owner_id == user_id:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Team owner must transfer ownership before being removed",
        )

    stmt = delete(UserRole).where(
        UserRole.team_id == team_id,
        UserRole.user_id == user_id,
    )
    result = await session.execute(stmt)

    if result.rowcount != 1:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User is not member of team",
        )

    await session.commit()