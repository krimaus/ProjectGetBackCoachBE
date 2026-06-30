from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth_util import encode_jwt, password_hash
from src.app.db_layer.orm_models.user import User
from src.app.service_layer.pydantic_models.auth import Token

async def authenticate_user(session: AsyncSession, username: str, password: str) -> Token:
    stmt = (
        select(User).where(User.username == username)
    )
    
    result = await session.scalars(stmt)
    user = result.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if not password_hash.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    encode = {
        'sub': user.username,
        'id': str(user.id),
        'exp': expires
    }
    
    return Token(
        access_token=await encode_jwt(encode),
        token_type="bearer",
    )