from typing import AsyncGenerator
from redis import Redis
from app.core.connections.cache import RedisClient

# Глобальный экземпляр клиента
redis_client = RedisClient()


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Dependency для получения Redis клиента в FastAPI.

    Yields:
        Redis: Экземпляр Redis клиента

    Usage:
        ```python
        @router.post("/auth/")
        async def authenticate(
            redis: Redis = Depends(get_redis_client)
        ):
            # Работа с Redis
        ```
    """
    client = await redis_client.connect() # или пул соединений? .get_connection()
    try:
        yield client
    finally:
        await redis_client.close() # убрать?
