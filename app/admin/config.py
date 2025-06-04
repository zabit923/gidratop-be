from starlette_admin.contrib.sqla import Admin

from app.core.connections.database import database_client

from .auth import CustomAuthProvider


def get_engine() -> None:
    """
    Получает глобальный engine базы данных.

    Returns:
        AsyncEngine: Глобальный engine базы данных
    """
    engine = database_client.get_engine()
    return engine


admin = Admin(
    engine=get_engine(),
    title="Admin Panel",
    auth_provider=CustomAuthProvider(),
)
