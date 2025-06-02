from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.connections.database import DatabaseClient

# Глобальный экземпляр клиента
database_client = DatabaseClient()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в FastAPI.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy

    Usage:
        ```python
        @router.post("/users/")
        async def create_user(
            user_data: UserCreate,
            session: AsyncSession = Depends(get_db_session)
        ):
            # Работа с сессией
        ```
    """
    session_factory = database_client.get_session_factory()

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
