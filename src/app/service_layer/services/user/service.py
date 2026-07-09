import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.db_layer.orm_models.user import User
from app.db_layer.orm_models.user_role import UserRole
from app.service_layer.pydantic_models import UserItem
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.service_layer.pydantic_models.user import CreateUserInput
from app.auth_util import password_hash


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
    
# TODO: ensure deleted user does not own any teams
# async def delete_user_service(session: AsyncSession, user_id: UUID) -> None:
#     stmt = select(UserRole.team_id).where(
#         UserRole.user_id == user_id,
#         UserRole.role == UserRoleEnum.OWNER,
#     )
#     result = await session.execute(stmt)
#     owned_team_ids = result.scalars().all()

#     if owned_team_ids:
#         raise HTTPException(
#             status.HTTP_409_CONFLICT,
#             detail=f"User owns {len(owned_team_ids)} team(s); transfer ownership before deleting",
#         )