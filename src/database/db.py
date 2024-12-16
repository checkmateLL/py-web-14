from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    """
    Dependency that creates a new database session for each request
    and closes it after the request is completed.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()