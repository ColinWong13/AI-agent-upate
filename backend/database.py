from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL, DATABASE_URL_SYNC, USE_SQLITE
from models.base import Base

if USE_SQLITE:
    async_engine = create_async_engine(DATABASE_URL, echo=False)
    sync_engine = create_engine(DATABASE_URL_SYNC, echo=False, connect_args={"check_same_thread": False})
else:
    async_engine = create_async_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=10)
    sync_engine = create_engine(DATABASE_URL_SYNC, echo=False)

AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
SyncSessionLocal = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
