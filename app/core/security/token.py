"""
Модуль для работы с токенами.

Предоставляет класс TokenManager для генерации, проверки и валидации JWT токенов.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Header
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from app.core.exceptions import (InvalidCredentialsError, TokenExpiredError,
                                 TokenInvalidError, TokenMissingError)
from app.core.settings import settings

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Класс для работы с JWT токенами.

    Предоставляет статические методы для генерации, проверки и валидации токенов.
    Поддерживает как access, так и refresh токены.
    """

    @staticmethod
    def generate_token(payload: dict) -> str:
        """
        Генерирует JWT токен.

        Args:
            payload: Данные для токена

        Returns:
            str: JWT токен
        """
        return jwt.encode(
            payload,
            key=settings.TOKEN_SECRET_KEY.get_secret_value(),
            algorithm=settings.TOKEN_ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Декодирует JWT токен.

        Args:
            token: JWT токен

        Returns:
            dict: Декодированные данные

        Raises:
            TokenExpiredError: Если токен просрочен
            TokenInvalidError: Если токен невалиден
        """
        try:
            return jwt.decode(
                token,
                key=settings.TOKEN_SECRET_KEY.get_secret_value(),
                algorithms=[settings.TOKEN_ALGORITHM],
            )
        except ExpiredSignatureError as error:
            raise TokenExpiredError() from error
        except JWTError as error:
            raise TokenInvalidError() from error

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Проверяет JWT токен и возвращает payload.

        Args:
            token: Токен пользователя

        Returns:
            dict: Данные пользователя

        Raises:
            TokenMissingError: Если токен отсутствует
        """
        if not token:
            raise TokenMissingError()
        return TokenManager.decode_token(token)

    @staticmethod
    def is_expired(expires_at: int) -> bool:
        """
        Проверяет, истек ли срок действия токена.

        Args:
            expires_at: Время истечения в секундах

        Returns:
            bool: True, если токен истек, иначе False
        """
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        return current_timestamp > expires_at

    @staticmethod
    def validate_token_payload(payload: dict, expected_type: Optional[str] = None) -> dict:
        """
        Универсальная валидация payload токена.

        Args:
            payload: Данные из токена
            expected_type: Ожидаемый тип токена (опционально)

        Returns:
            dict: Валидированный payload

        Raises:
            TokenInvalidError: Если тип токена не совпадает
            TokenExpiredError: Если токен истек
        """
        # Проверяем тип токена (если указан)
        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type:
                logger.warning(
                    "Неверный тип токена",
                    extra={"expected": expected_type, "actual": token_type}
                )
                raise TokenInvalidError(f"Ожидался тип токена: {expected_type}")

        # Проверяем срок действия
        expires_at = payload.get("expires_at")
        if TokenManager.is_expired(expires_at):
            logger.warning("Токен истек", extra={"expires_at": expires_at})
            raise TokenExpiredError()

        return payload

    # Методы токенов доступа и обновления
    @staticmethod
    def create_payload(user: Any) -> dict:
        """
        Создает payload для access токена.

        Args:
            user: Данные пользователя

        Returns:
            dict: Payload для JWT
        """
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + TokenManager.get_token_expiration()
        )
        return {
            "sub": user.email,
            "expires_at": expires_at,
            "user_id": user.id,
            "is_verified": user.is_verified,
            "role": user.role,
        }

    @staticmethod
    def get_token_expiration() -> int:
        """
        Получает время истечения срока действия access токена в секундах.

        Returns:
            int: Количество секунд до истечения токена

        Example:
            15 минут * 60 = 900 секунд
        """
        return settings.TOKEN_EXPIRE_MINUTES * 60

    @staticmethod
    def validate_payload(payload: dict) -> str:
        """
        Валидирует данные из payload access токена.

        Args:
            payload: Данные пользователя

        Returns:
            str: Email пользователя

        Raises:
            InvalidCredentialsError: Если email отсутствует
            TokenExpiredError: Если токен просрочен
        """
        TokenManager.validate_token_payload(payload)

        email = payload.get("sub")
        if not email:
            raise InvalidCredentialsError()

        return email


    # Методы refresh токена

    @staticmethod
    def create_refresh_payload(user_id: int) -> dict:
        """
        Создает payload для refresh токена.

        Args:
            user_id: ID пользователя

        Returns:
            dict: Payload для JWT refresh токена
        """
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Дни в секунды
        )
        return {
            "sub": str(user_id),
            "expires_at": expires_at,
            "type": "refresh",
        }

    @staticmethod
    def validate_refresh_token(payload: dict) -> int:
        """
        Валидирует данные из payload refresh токена.

        Args:
            payload: Данные из токена

        Returns:
            int: ID пользователя

        Raises:
            TokenInvalidError: Если тип токена не refresh или отсутствует user_id
            TokenExpiredError: Если токен просрочен
        """
        TokenManager.validate_token_payload(payload, "refresh")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в refresh токене")

        return int(user_id)

    # Методы токенов верификации

    @staticmethod
    def generate_verification_token(user_id: int) -> str:
        """
        Генерирует токен для подтверждения email

        Args:
            user_id: Идентификатор пользователя

        Returns:
            str: Токен для подтверждения email
        """
        from app.core.settings import settings

        expires_at = int(datetime.now(timezone.utc).timestamp()) + (
            settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60
        )
        payload = {
            "sub": str(user_id),
            "type": "email_verification",
            "expires_at": expires_at,
        }
        return TokenManager.generate_token(payload)

    @staticmethod
    def validate_verification_token(payload: dict) -> int:
        """
        Валидирует токен верификации email.

        Args:
            payload: Данные из токена

        Returns:
            int: ID пользователя

        Raises:
            TokenInvalidError: Если тип токена неверный
            TokenExpiredError: Если токен истек
        """
        # Используем универсальную валидацию с проверкой типа
        TokenManager.validate_token_payload(payload, "email_verification")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в токене верификации")

        return int(user_id)

    # Методы токенов востановления пароля
    @staticmethod
    def generate_password_reset_token(user_id: int) -> str:
        """
        Генерирует токен для сброса пароля.

        Args:
            user_id: ID пользователя

        Returns:
            str: Токен для сброса пароля
        """
        payload = {
            "sub": str(user_id),
            "type": "password_reset",
            "expires_at": (
                int(datetime.now(timezone.utc).timestamp())
                + 1800  # 30 минут (в секундах)
            ),
        }
        return TokenManager.generate_token(payload)

    @staticmethod
    def validate_password_reset_token(payload: dict) -> int:
        """
        Валидирует токен сброса пароля.

        Args:
            payload: Данные из токена

        Returns:
            int: ID пользователя

        Raises:
            TokenInvalidError: Если тип токена неверный
            TokenExpiredError: Если токен истек
        """
        # Используем универсальную валидацию с проверкой типа
        TokenManager.validate_token_payload(payload, "password_reset")

        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError("Отсутствует user_id в токене сброса пароля")

        return int(user_id)

    # Прочие методы токенов
    @staticmethod
    def get_token_from_header(
        authorization: str = Header(
            None, description="Заголовок Authorization с токеном Bearer"
        )
    ) -> str:
        """
        Получение токена из заголовка Authorization.

        Args:
            authorization: Заголовок Authorization из запроса

        Returns:
            str: Извлеченный токен

        Raises:
            TokenMissingError: Если заголовок Authorization отсутствует
            TokenInvalidError: Если формат заголовка неверный
        """
        if not authorization:
            raise TokenMissingError()

        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer":
            raise TokenInvalidError()

        if not token:
            raise TokenMissingError()

        return token
