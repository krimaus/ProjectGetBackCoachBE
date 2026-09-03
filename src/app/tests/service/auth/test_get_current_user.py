import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth_util import get_current_user


def _make_token(claims: dict, secret: str | None = None, algorithm: str | None = None) -> str:
    secret = secret or os.getenv("SECRET_KEY")
    algorithm = algorithm or os.getenv("ALGORITHM")
    return jwt.encode(claims, secret, algorithm=algorithm)


@pytest.mark.asyncio
async def test_get_current_user_valid_token_returns_username_and_id():
    user_id = uuid.uuid4()
    token = _make_token({
        "sub": "testuser",
        "id": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    })

    result = await get_current_user(token)

    assert result == {"username": "testuser", "id": user_id}


@pytest.mark.asyncio
async def test_get_current_user_expired_token_raises_401_token_expired():
    token = _make_token({
        "sub": "testuser",
        "id": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    })

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expired"


@pytest.mark.asyncio
async def test_get_current_user_bad_signature_raises_401_could_not_validate():
    token = _make_token(
        {
            "sub": "testuser",
            "id": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        secret="a-completely-wrong-secret",
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_malformed_token_raises_401_could_not_validate():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("not-a-valid-jwt-at-all")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_missing_username_claim_raises_401():
    token = _make_token({
        "id": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    })

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_missing_id_claim_raises_401():
    token = _make_token({
        "sub": "testuser",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    })

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_malformed_id_claim_raises_401():
    token = _make_token({
        "sub": "testuser",
        "id": "not-a-uuid",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    })

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"