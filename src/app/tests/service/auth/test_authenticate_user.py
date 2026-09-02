import os

from fastapi import HTTPException
from jose import jwt
import pytest

from app.db_layer.orm_models.user import User
from app.service_layer.services.auth.service import authenticate_user
from app.auth_util import password_hash


async def test_authenticate_user_success(async_session, persisted_user):
    user, plain_password = persisted_user

    token = await authenticate_user(async_session, user.username, plain_password)

    assert token.token_type == "bearer"

    payload = jwt.decode(
        token.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
    )
    assert payload["sub"] == user.username
    assert payload["id"] == str(user.id)


async def test_authenticate_user_wrong_password(async_session, persisted_user):
    user, _ = persisted_user

    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(async_session, user.username, "wrong-password")

    assert exc_info.value.status_code == 401


async def test_authenticate_user_unknown_username(async_session):
    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(async_session, "does-not-exist", "anything")

    assert exc_info.value.status_code == 401
    
    
async def test_authenticate_user_errors_are_indistinguishable(async_session, persisted_user):
    user, _ = persisted_user

    with pytest.raises(HTTPException) as wrong_pw:
        await authenticate_user(async_session, user.username, "wrong-password")
    with pytest.raises(HTTPException) as unknown_user:
        await authenticate_user(async_session, "nonexistent", "anything")

    assert wrong_pw.value.detail == unknown_user.value.detail