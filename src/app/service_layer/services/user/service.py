import uuid

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.service_layer.pydantic_models import UserItem
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from src.app.service_layer.pydantic_models.user import CreateUserInput, UpdateUserInput
from app.auth_util import password_hash
from src.app.service_layer.pydantic_models.user_role import UserRoleItem


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
        await session.refresh(user) # read all DB generated fields
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    return UserItem(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
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
        username=user.username
    )
    
    
async def get_user_service(session: AsyncSession, user_id: uuid.UUID) -> UserItem:
    stmt = select(User).where(User.id == user_id)
    
    result = await session.execute(stmt)
    user = result.scalars().one()
    
    return UserItem(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
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