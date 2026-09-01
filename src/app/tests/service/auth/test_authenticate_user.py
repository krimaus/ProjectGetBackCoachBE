import os
import uuid

from fastapi import HTTPException
from jose import jwt
import pytest

from src.app.db_layer.orm_models.user import User
from src.app.service_layer.services.auth.service import authenticate_user
from app.auth_util import password_hash


async def test_authenticate_user_success(async_session):
    plain_password = "correct-horse-battery-staple"
    user = User(
        id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        username="testuser",
        hashed_password=password_hash.hash(plain_password),
    )
    async_session.add(user)
    await async_session.flush()

    token = await authenticate_user(async_session, user.username, plain_password)

    assert token.token_type == "bearer"

    payload = jwt.decode(
        token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
    )
    assert payload["sub"] == user.username
    assert payload["id"] == str(user.id)


async def test_authenticate_user_wrong_password(async_session):
    plain_password = "correct-horse-battery-staple"
    user = User(
        id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        username="testuser",
        hashed_password=password_hash.hash(plain_password),
    )
    async_session.add(user)
    await async_session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(async_session, user.username, "wrong-password")

    assert exc_info.value.status_code == 401


async def test_authenticate_user_unknown_username(async_session):
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(async_session, "does-not-exist", "anything")

    assert exc_info.value.status_code == 401