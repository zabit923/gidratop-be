"""
Схемы данных для регистрации пользователей.

Содержит классы данных, которые помещаются в поле `data` ответов API.
Эти схемы описывают структуру полезной нагрузки ответов регистрации.
"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseCommonResponseSchema


class RegistrationDataSchema(BaseCommonResponseSchema):
    """
    Схема данных пользователя при успешной регистрации.

    Содержит основную информацию о зарегистрированном пользователе,
    которая безопасна для передачи клиенту. Исключает конфиденциальные
    данные такие как хешированный пароль.

    Attributes:
        user_id: Уникальный идентификатор пользователя в системе
        username: Имя пользователя для входа в систему
        email: Email адрес пользователя
        role: Роль пользователя в системе (по умолчанию "user")
        is_active: Статус активности аккаунта
        is_verified: Статус верификации email (False при регистрации)
        created_at: Дата и время создания аккаунта
        referral_code: Реферальный код пользователя
        access_token: Ограниченный JWT токен доступа (до верификации)
        refresh_token: JWT токен для обновления access токена
        token_type: Тип токена (всегда "bearer")
        requires_verification: Флаг необходимости верификации email

    Example:
        ```python
        {
            "user_id": 123,
            "username": "john_doe",
            "email": "john@example.com",
            "role": "user",
            "is_active": true,
            "is_verified": false,
            "created_at": "2024-01-15T10:30:00Z",
            "referral_code": "REF12345678",
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "requires_verification": true
        }
        ```
    """

    user_id: int = Field(
        description="Уникальный идентификатор пользователя", examples=[123, 456, 789]
    )

    username: str = Field(
        description="Имя пользователя для входа в систему",
        examples=["john_doe", "user123", "admin"],
    )

    email: EmailStr = Field(
        description="Email адрес пользователя",
        examples=["user@example.com", "john.doe@company.org"],
    )

    role: str = Field(
        default="user",
        description="Роль пользователя в системе",
        examples=["user", "admin", "moderator"],
    )

    is_active: bool = Field(
        default=True, description="Статус активности аккаунта пользователя"
    )

    is_verified: bool = Field(
        default=False, description="Статус верификации email или телефона"
    )

    created_at: datetime = Field(
        description="Дата и время создания аккаунта", examples=["2024-01-15T10:30:00Z"]
    )

    referral_code: str | None = Field(
        default=None,
        description="Реферальный код пользователя для приглашения других",
        examples=["REF123ABC", "INVITE456", None],
    )

    access_token: str = Field(
        description="Ограниченный JWT токен доступа (до верификации email)",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."]
    )

    refresh_token: str = Field(
        description="JWT токен для обновления access токена",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."]
    )

    token_type: str = Field(
        default="bearer",
        description="Тип токена (всегда bearer)"
    )

    requires_verification: bool = Field(
        default=True,
        description="Требуется ли верификация email для полного доступа"
    )

class VerificationDataSchema(BaseCommonResponseSchema):
    """
    Данные верификации email адреса.

    Содержит информацию о результате подтверждения email
    и новые полные токены доступа после верификации.

    Attributes:
        user_id: ID верифицированного пользователя
        email: Верифицированный email адрес
        verified_at: Время подтверждения email в UTC
        access_token: Новый полный JWT токен доступа (без ограничений)
        refresh_token: Новый JWT токен для обновления
        token_type: Тип токена (всегда "bearer")

    Example:
        ```json
        {
            "user_id": 123,
            "email": "john@example.com",
            "verified_at": "2024-01-15T10:35:00Z",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        ```
    """

    user_id: int = Field(
        description="Идентификатор верифицированного пользователя",
        example=123
    )
    email: EmailStr = Field(
        description="Верифицированный email адрес",
        example="john@example.com"
    )
    verified_at: datetime = Field(
        description="Время подтверждения email в формате UTC",
        example="2024-01-15T10:35:00Z",
    )
    access_token: str = Field(
        description="Новый полный JWT токен доступа (без ограничений)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    refresh_token: str = Field(
        description="Новый JWT токен для обновления access токена",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена (всегда bearer)"
    )


class ResendVerificationDataSchema(BaseCommonResponseSchema):
    """
    Данные повторной отправки письма верификации.

    Содержит информацию о повторной отправке письма подтверждения.
    Возвращается при запросе на повторную отправку токена верификации.

    Attributes:
        email: Email адрес, на который отправлено письмо
        sent_at: Время отправки письма
        expires_in: Время действия токена в секундах
    """

    email: EmailStr = Field(
        description="Email адрес для повторной отправки", example="john@example.com"
    )
    sent_at: datetime = Field(
        description="Время отправки письма в формате UTC",
        example="2024-01-15T10:40:00Z",
    )
    expires_in: int = Field(
        description="Время действия токена верификации в секундах", example=3600
    )

class VerificationStatusDataSchema(BaseCommonResponseSchema):
    """
    Данные статуса верификации email.

    Содержит информацию о текущем статусе верификации
    email адреса пользователя.

    Attributes:
        email: Проверяемый email адрес
        is_verified: Статус верификации (true/false)
        checked_at: Время проверки статуса в UTC

    Example:
        ```json
        {
            "email": "john@example.com",
            "is_verified": true,
            "checked_at": "2024-01-15T10:45:00Z"
        }
        ```
    """
    email: EmailStr = Field(
        description="Проверяемый email адрес",
        example="john@example.com"
    )
    is_verified: bool = Field(
        description="Статус верификации email",
        example=True
    )
    checked_at: datetime = Field(
        description="Время проверки статуса в UTC",
        example="2024-01-15T10:45:00Z"
    )