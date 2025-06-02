from typing import AsyncGenerator
from app.core.connections.s3 import S3ContextManager


async def get_s3_client() -> AsyncGenerator:
    """
    Dependency для получения S3 клиента.
    
    Yields:
        S3 клиент для работы с хранилищем
    """
    async with S3ContextManager() as s3_client:
        yield s3_client
