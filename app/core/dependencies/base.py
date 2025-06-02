from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar

T = TypeVar('T')

@asynccontextmanager
async def managed_client(client_factory) -> AsyncGenerator[T, None]:
    """
    Универсальный контекстный менеджер для клиентов

    !TODO: зайдействовать
    """
    client = None
    try:
        client = await client_factory()
        yield client
    except Exception:
        if hasattr(client, 'rollback'):
            await client.rollback()
        raise
    finally:
        if hasattr(client, 'close'):
            await client.close()
