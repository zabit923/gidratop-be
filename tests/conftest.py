"""
Конфигурация для тестов pytest.
Содержит фикстуры для настройки тестового окружения.
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.v1.base import BaseModel
from app.core.dependencies import get_db_session, database_client
from app.core.settings import settings


class TestDatabase:
    """Класс для управления тестовой базой данных"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.session = None
    
    async def setup(self):
        """Настройка тестовой БД"""
        # Получаем URL тестовой БД
        db_url = settings.database_url.replace("gidrator_db", "gidrator_db_test")
        
        # Создаем движок
        self.engine = create_async_engine(
            db_url,
            echo=False,  # Отключаем логи SQL в тестах
            future=True
        )
        
        # Создаем фабрику сессий
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Создаем все таблицы
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
    
    async def get_session(self):
        """Получить сессию БД"""
        if not self.session_factory:
            await self.setup()
        
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()
    
    async def cleanup(self):
        """Очистка после тестов"""
        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.drop_all)
            await self.engine.dispose()

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
        settings.POSTGRES_DB, f"{settings.POSTGRES_DB}_test"
    )
    
    engine = create_async_engine(
        test_database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in test_database_url else {},
        echo=False,
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
        # Начинаем транзакцию
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Откатываем транзакцию после каждого теста
            await transaction.rollback()
            await session.close()

@pytest_asyncio.fixture
async def client(db_session):
    """Создает тестовый HTTP клиент."""
    
    async def override_get_db():
        yield db_session
    
    # Переопределяем зависимость
    app.dependency_overrides[get_db_session] = override_get_db
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://localhost"
        ) as ac:
            yield ac
    finally:
        # Очищаем переопределения после теста
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def setup_database():
    """Автоматически настраивает базу данных для каждого теста."""
    await database_client.connect()
    yield
    await database_client.close()