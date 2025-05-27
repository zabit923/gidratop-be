import logging
from typing import Any, Dict, List

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.lifespan import lifespan
from app.core.settings.logging import LoggingSettings
from app.core.settings.paths import PathSettings

env_file_path, app_env = PathSettings.get_env_file_and_type()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Настройки приложения

    """

    # Виртуальное окружение приложения
    app_env: str = app_env

    logging: LoggingSettings = LoggingSettings()
    paths: PathSettings = PathSettings()

    # Настройки приложения
    TITLE: str = "Gidrator"
    DESCRIPTION: str = ""
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def app_params(self) -> dict:
        """
        Параметры для инициализации FastAPI приложения.

        Returns:
            Dict с настройками FastAPI
        """
        return {
            "title": self.TITLE,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
            "root_path": "",
            "lifespan": lifespan,
        }

    @property
    def uvicorn_params(self) -> dict:
        """
        Параметры для запуска uvicorn сервера.

        Returns:
            Dict с настройками uvicorn
        """
        return {
            "host": self.HOST,
            "port": self.PORT,
            "proxy_headers": True,
            "log_level": "debug",
        }

    # Настройки базы данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @property
    def database_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @property
    def database_url(self) -> str:
        """
        Для alembic нужно строку с подключением к БД
        """
        database_dsn = str(self.database_dsn)
        return database_dsn

    @property
    def engine_params(self) -> Dict[str, Any]:
        """
        Формирует параметры для создания SQLAlchemy engine
        """
        return {
            "echo": True,
        }

    @property
    def session_params(self) -> Dict[str, Any]:
        """
        Формирует параметры для создания SQLAlchemy session
        """
        return {
            "autocommit": False,
            "autoflush": False,
            "expire_on_commit": False,
            "class_": AsyncSession,
        }

    # Настройки CORS
    ALLOW_ORIGINS: List[str] = []
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    @property
    def cors_params(self) -> Dict[str, Any]:
        """
        Формирует параметры CORS для FastAPI.

        Returns:
            Dict с настройками CORS middleware
        """
        return {
            "allow_origins": self.ALLOW_ORIGINS,
            "allow_credentials": self.ALLOW_CREDENTIALS,
            "allow_methods": self.ALLOW_METHODS,
            "allow_headers": self.ALLOW_HEADERS,
        }

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )
