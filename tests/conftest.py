"""
Конфигурация для тестов pytest.
Содержит фикстуры для настройки тестового окружения.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.connections.database import database_client
from app.dependencies import get_db_session
from app.core.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Создает тестовый движок базы данных."""
    # Используем in-memory SQLite для тестов или отдельную тестовую БД
    test_database_url = settings.database_url.replace(
        settings.postgres_db, f"{settings.postgres_db}_test"
    )
    
    engine = create_async_engine(
        test_database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in test_database_url else {},
        echo=True,
    )
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_engine):
    """Создает фабрику сессий для тестов."""
    # Создаем таблицы в тестовой БД
    from app.models.v1.base import BaseModel
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    yield session_factory
    
    # Очищаем таблицы после тестов
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_session_factory):
    """Создает сессию БД для каждого теста."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """Создает тестовый HTTP клиент."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def setup_database():
    """Автоматически настраивает базу данных для каждого теста."""
    await database_client.connect()
    yield
    await database_client.close()