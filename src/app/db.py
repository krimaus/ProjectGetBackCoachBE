import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

load_dotenv()

db_string = f"{os.getenv('SQLALCHEMY_DB_TYPE')}://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_async_engine(
    db_string,
    echo=True,
    future=True
)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

async def get_session() -> AsyncSession:
    return await session_maker()