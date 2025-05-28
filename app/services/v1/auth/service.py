"""
Сервис аутентификации пользователей.

Обеспечивает аутентификацию, создание токенов и управление сессиями.
"""
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ForbiddenError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UserNotFoundError
)
from app.core.security.password import PasswordHasher
from app.core.security.token import TokenManager

from app.schemas.v1.auth import (
    AuthSchema,
    TokenResponseSchema,
    LogoutResponseSchema,
    PasswordResetResponseSchema,
    PasswordResetConfirmResponseSchema
)
from app.schemas.v1.users import UserCredentialsSchema
from app.services.v1.base import BaseService
from .data_manager import AuthDataManager


class AuthService(BaseService):
    """
    Сервис для аутентификации пользователей.

    Предоставляет методы для:
    - Аутентификации пользователей
    - Создания и обновления JWT токенов
    - Выхода из системы
    - Восстановления пароля (заглушки)

    Attributes:
        session: Асинхронная сессия базы данных
        data_manager: Менеджер данных для аутентификации
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис аутентификации.

        Args:
            session: Асинхронная сессия базы данных
        """
        super().__init__(session)
        self.data_manager = AuthDataManager(session)

    async def authenticate(
        self, form_data: OAuth2PasswordRequestForm
    ) -> TokenResponseSchema:
        """
        Аутентифицирует пользователя по логину и паролю.

        Args:
            form_data: Данные для аутентификации пользователя

        Returns:
            TokenResponseSchema: Токены доступа

        Raises:
            InvalidCredentialsError: Если пользователь не найден или пароль неверный
            ForbiddenError: Если аккаунт деактивирован
        """
        credentials = AuthSchema(
            username=form_data.username,
            password=form_data.password
        )

        identifier = credentials.username

        self.logger.info(
            "Попытка аутентификации",
            extra={
                "identifier": identifier,
                "has_password": bool(credentials.password),
            },
        )

        # Ищем пользователя по email, телефону или имени пользователя
        user_model = await self.data_manager.get_user_by_identifier(identifier)

        self.logger.info(
            "Начало аутентификации",
            extra={"identifier": identifier, "user_found": bool(user_model)},
        )

        if not user_model:
            self.logger.warning(
                "Пользователь не найден",
                extra={"identifier": identifier}
            )
            raise InvalidCredentialsError()

        # Проверяем активность аккаунта
        if not user_model.is_active:
            self.logger.warning(
                "Попытка входа в неактивный аккаунт",
                extra={"identifier": identifier, "user_id": user_model.id},
            )
            raise ForbiddenError(
                detail="Аккаунт деактивирован",
                extra={"identifier": credentials.username},
            )

        # Проверяем пароль
        if not PasswordHasher.verify(user_model.hashed_password, credentials.password):
            self.logger.warning(
                "Неверный пароль",
                extra={"identifier": identifier, "user_id": user_model.id},
            )
            raise InvalidCredentialsError()

        # Создаем схему пользователя для токена
        user_schema = UserCredentialsSchema.model_validate(user_model)

        if not user_schema.is_verified:
            self.logger.warning(
                "Вход с неподтвержденным аккаунтом",
                extra={"identifier": identifier, "user_id": user_model.id},
            )

        self.logger.info(
            "Аутентификация успешна",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
                "role": user_schema.role,
            },
        )

        await self.data_manager.update_items(
            user_schema.id,
            {"last_login": datetime.now(timezone.utc)}
        )

        # Создаем токены
        access_token = await self.create_token(user_schema)
        refresh_token = await self.create_refresh_token(user_schema.id)

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def create_token(self, user_schema: UserCredentialsSchema) -> str:
        """
        Создание JWT access токена.

        Args:
            user_schema: Данные пользователя

        Returns:
            str: Access токен
        """
        payload = TokenManager.create_payload(user_schema)

        self.logger.debug(
            "Создан payload токена",
            extra={"payload": payload}
        )

        access_token = TokenManager.generate_token(payload)

        self.logger.debug(
            "Сгенерирован токен",
            extra={"access_token_length": len(access_token)}
        )

        # TODO: Сохранить токен в Redis когда будет готов

        self.logger.info(
            "Токен создан",
            extra={
                "user_id": user_schema.id,
                "access_token_length": len(access_token)
            },
        )

        return access_token

    async def create_refresh_token(self, user_id: int) -> str:
        """
        Создание JWT refresh токена.

        Args:
            user_id: ID пользователя

        Returns:
            str: Refresh токен
        """
        payload = TokenManager.create_refresh_payload(user_id)

        self.logger.debug(
            "Создан payload refresh токена",
            extra={"payload": payload}
        )

        refresh_token = TokenManager.generate_token(payload)

        self.logger.debug(
            "Сгенерирован refresh токен",
            extra={"refresh_token_length": len(refresh_token)}
        )

        # TODO: Сохранить refresh токен в Redis когда будет готов

        self.logger.info(
            "Refresh токен создан",
            extra={
                "user_id": user_id,
                "refresh_token_length": len(refresh_token)
            },
        )

        return refresh_token

    async def refresh_token(self, refresh_token: str) -> TokenResponseSchema:
        """
        Обновляет access токен с помощью refresh токена.

        Args:
            refresh_token: Refresh токен

        Returns:
            TokenResponseSchema: Новые токены доступа

        Raises:
            TokenInvalidError: Если refresh токен недействителен
            TokenExpiredError: Если refresh токен истек
            UserNotFoundError: Если пользователь не найден
        """
        try:
            # Декодируем refresh токен
            payload = TokenManager.decode_token(refresh_token)

            # Валидируем refresh токен
            user_id = TokenManager.validate_refresh_token(payload)

            # TODO: Проверить refresh токен в Redis когда будет готов

            # Получаем пользователя
            user_model = await self.data_manager.get_model_by_field("id", user_id)

            if not user_model:
                self.logger.warning(
                    "Пользователь не найден при обновлении токена",
                    extra={"user_id": user_id},
                )
                raise UserNotFoundError(field="id", value=user_id)

            user_schema = UserCredentialsSchema.model_validate(user_model)

            # Создаем новые токены
            access_token = await self.create_token(user_schema)
            new_refresh_token = await self.create_refresh_token(user_id)

            # TODO: Удалить старый refresh токен из Redis

            self.logger.info(
                "Токены успешно обновлены",
                extra={"user_id": user_id},
            )

            return TokenResponseSchema(
                access_token=access_token,
                refresh_token=new_refresh_token
            )

        except (TokenExpiredError, TokenInvalidError) as e:
            self.logger.warning(
                "Ошибка при обновлении токена: %s",
                type(e).__name__,
                extra={"error_type": type(e).__name__}
            )
            raise

    async def logout(self, access_token: str) -> LogoutResponseSchema:
        """
        Выполняет выход пользователя из системы.

        Args:
            access_token: Access токен пользователя

        Returns:
            LogoutResponseSchema: Подтверждение выхода
        """
        try:
            # Декодируем токен для получения user_id
            payload = TokenManager.decode_token(access_token)
            user_id = payload.get("sub")

            # TODO: Удалить токены из Redis когда будет готов
            # TODO: Установить статус offline в Redis

            self.logger.info(
                "Пользователь вышел из системы",
                extra={"user_id": user_id}
            )

            return LogoutResponseSchema(
                message="Выход выполнен успешно"
            )

        except Exception as e:
            self.logger.error(
                "Ошибка при выходе из системы",
                extra={"error": str(e)}
            )
            # Даже если произошла ошибка, считаем выход успешным
            return LogoutResponseSchema(
                message="Выход выполнен"
            )

    # Заглушки для восстановления пароля
    async def send_password_reset_email(self, email: str) -> PasswordResetResponseSchema:
        """
        Отправляет email со ссылкой для сброса пароля.

        ЗАГЛУШКА: Пока что только логирует запрос.

        Args:
            email: Email адрес пользователя

        Returns:
            PasswordResetResponseSchema: Подтверждение отправки
        """
        self.logger.info(
            "Запрос восстановления пароля (заглушка)",
            extra={"email": email}
        )

        # TODO: Реализовать отправку email

        return PasswordResetResponseSchema(
            message="Если аккаунт с таким email существует, письмо будет отправлено"
        )

    async def reset_password(
        self, token: str, new_password: str
    ) -> PasswordResetConfirmResponseSchema:
        """
        Устанавливает новый пароль по токену сброса.

        ЗАГЛУШКА: Пока что только логирует запрос.

        Args:
            token: Токен сброса пароля
            new_password: Новый пароль

        Returns:
            PasswordResetConfirmResponseSchema: Подтверждение сброса
        """
        self.logger.info(
            "Сброс пароля (заглушка)",
            extra={"token_length": len(token)}
        )

        # TODO: Реализовать сброс пароля

        return PasswordResetConfirmResponseSchema(
            message="Пароль успешно изменен"
        )
