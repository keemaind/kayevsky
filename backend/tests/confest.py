import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Тестовая БД в памяти"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """Сессия для каждого теста"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine):
    """AsyncClient с переопределением БД"""

    async def override_get_db():
        async_session = sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[app.database.get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
