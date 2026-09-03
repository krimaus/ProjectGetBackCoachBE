import os
from unittest.mock import AsyncMock
import uuid
from httpx import ASGITransport
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from app.db_layer.orm_models.common.base import Base
from app.main import app
from app.db import get_session
import psycopg2
from psycopg2 import sql

from app.auth_util import get_current_user
from app.db_layer.orm_models.enums.user_role_enum import UserRoleEnum
from app.db_layer.orm_models.user import User
from app.auth_util import password_hash


TEST_DB_NAME = os.getenv("TEST_DB_NAME")
TEST_DB_USER = os.getenv("TEST_DB_USER")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD")
TEST_DB_HOST = os.getenv("TEST_DB_HOST")
TEST_DB_PORT = os.getenv("TEST_DB_PORT")


def create_test_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
    )
    
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (TEST_DB_NAME,),
        )
        exists = cur.fetchone()

        if not exists:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(TEST_DB_NAME)
                )
            )

    conn.close()
  
    
def drop_test_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
    )
    
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s
            AND pid <> pg_backend_pid()
            """,
            (TEST_DB_NAME,),
        )

        cur.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier(TEST_DB_NAME)
            )
        )

    conn.close()
    
    
@pytest.fixture(scope="session")
def setup_test_db():
    create_test_database()
    yield
    drop_test_database()


@pytest.fixture(scope="session")
async def engine(setup_test_db):
    engine = create_async_engine(
        f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}"
        f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}",
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def async_session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        
        session = AsyncSession(bind=conn, expire_on_commit=False)
        await conn.begin_nested()

        yield session

        await session.close()
        await conn.rollback()


@pytest.fixture
async def client(async_session):
    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    from httpx import AsyncClient
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    

@pytest.fixture
def test_user():
    return {"username": "testuser", "id": uuid.uuid4()}


@pytest.fixture
async def authorized_client(client, test_user):
    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield client

    app.dependency_overrides.pop(get_current_user, None)
    
    
@pytest.fixture
def mock_user_role(monkeypatch):
    def _apply(role: UserRoleEnum | None, target: str):
        mock = AsyncMock(return_value=role)
        monkeypatch.setattr(target, mock)
        return mock
    return _apply


@pytest.fixture
async def persisted_user(async_session):
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
    return user, plain_password