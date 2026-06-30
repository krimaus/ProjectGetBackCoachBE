from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.app.db_layer.orm_models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.app.service_layer.pydantic_models.user import CreateUserInput, UserItem
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