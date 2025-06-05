"""Конфигурация для тестов pytest."""
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models.v1.base import BaseModel
from app.models.v1.users import UserRole
from app.core.dependencies import get_db_session
from app.core.security.auth import get_current_user
from app.core.settings import settings
from app.schemas import CurrentUserSchema


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Тестовый движок БД."""
    test_db_url = settings.database_url.replace(
        settings.POSTGRES_DB,
        f"{settings.POSTGRES_DB}_test"
    )

    engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_pre_ping=True
    )

    import asyncpg

    async def create_test_db():
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD.get_secret_value(),
            database='postgres'
        )

        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                f"{settings.POSTGRES_DB}_test"
            )

            if not exists:
                await conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}_test"')
        finally:
            await conn.close()

    await create_test_db()

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def session_factory(test_engine):
    """Фабрика сессий для тестов."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_session(session_factory):
    """Сессия БД для каждого теста."""
    async with session_factory() as session:
        transaction = await session.begin()

        try:
            yield session
        finally:
            await transaction.rollback()


@pytest_asyncio.fixture
async def mock_user():
    """Мок пользователя для тестов."""
    return CurrentUserSchema(
        id=1,
        username="testuser",
        email="test@example.com",
        role=UserRole.USER,
        is_active=True,
        is_verified=True
    )


@pytest_asyncio.fixture
async def client(db_session):
    """HTTP клиент для тестов."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver"
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client, mock_user):
    """HTTP клиент с мокированной аутентификацией."""
    async def mock_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = mock_get_current_user

    try:
        yield client
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
