import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db_layer.orm_models.common.base import Base
from app.main import app
from app.db import get_session
import psycopg2

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
        autocommit=True,
    )

    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (TEST_DB_NAME,),
        )
        exists = cur.fetchone()

        if not exists:
            cur.execute(
                psycopg2.sql.SQL("CREATE DATABASE {}").format(
                    psycopg2.sql.Identifier(TEST_DB_NAME)
                )
            )

    conn.close()
    
@pytest.fixture(scope="session")
def setup_test_db():
    create_test_database()

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
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def client(engine):
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_session():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()