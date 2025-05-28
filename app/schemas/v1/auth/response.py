"""
Схемы ответов для аутентификации.

Содержит Pydantic схемы для исходящих данных endpoints аутентификации.
"""
from typing import Optional
from pydantic import EmailStr, Field
from datetime import datetime

from app.schemas.v1.base import BaseResponseSchema


class TokenResponseSchema(BaseResponseSchema):
    """
    Схема ответа с токенами.

    Attributes:
        access_token: JWT токен доступа
        refresh_token: Refresh токен
        token_type: Тип токена (Bearer)
        expires_in: Время жизни access токена в секундах
    """

    access_token: str = Field(description="JWT токен доступа")
    refresh_token: str = Field(description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(default=900, description="Время жизни токена в секундах")
    message: str = "Аутентификация успешна"


class LogoutResponseSchema(BaseResponseSchema):
    """
    Схема ответа при выходе из системы.

    Attributes:
        logged_out_at: Время выхода из системы
    """

    logged_out_at: datetime
    message: str = "Выход из системы выполнен успешно"


class PasswordResetResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос восстановления пароля.

    Attributes:
        email: Email, на который отправлена ссылка
        expires_in: Время действия токена в секундах
    """

    email: EmailStr = Field(description="Email адрес для восстановления пароля")
    expires_in: int = Field(default=3600, description="Время действия токена в секундах")
    message: str = "Ссылка для восстановления пароля отправлена на email"


class PasswordResetConfirmResponseSchema(BaseResponseSchema):
    """
    Схема ответа на успешный сброс пароля.

    Attributes:
        password_changed_at: Время изменения пароля
    """

    password_changed_at: datetime
    message: str = "Пароль успешно изменен"
