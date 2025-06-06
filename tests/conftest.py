"""Конфигурация для тестов pytest."""
from unittest.mock import AsyncMock, patch
import pytest_asyncio
import asyncpg
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.main import app
from app.models.v1.base import BaseModel
from app.models.v1.users import UserRole
from app.core.dependencies import get_db_session
from app.core.security.auth import get_current_user
from app.core.settings import settings
from app.schemas import CurrentUserSchema


@pytest_asyncio.fixture
async def test_engine():
    """Тестовый движок БД."""
    test_db_name = f"{settings.POSTGRES_DB}_test"

    # Создаем тестовую БД
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD.get_secret_value(),
        database='postgres'
    )

    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
        await conn.execute(f'CREATE DATABASE "{test_db_name}"')
    finally:
        await conn.close()

    # Создаем движок без connection pool для тестов
    test_db_url = settings.database_url.replace(
        settings.POSTGRES_DB, test_db_name
    )

    engine = create_async_engine(
        test_db_url,
        echo=False,
        poolclass=NullPool,  # Отключаем pool для тестов
    )

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    # Очистка
    await engine.dispose()

    # Удаляем тестовую БД
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD.get_secret_value(),
        database='postgres'
    )
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Изолированная сессия БД для каждого теста."""
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(
        bind=connection,
        expire_on_commit=False
    )

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


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

@pytest_asyncio.fixture(autouse=True)
async def mock_messaging():
    """Мокает messaging для тестов."""
    with patch('app.core.integrations.messaging.producers.broker.publish') as mock_publish:
        mock_publish.return_value = AsyncMock()
        yield mock_publish

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
