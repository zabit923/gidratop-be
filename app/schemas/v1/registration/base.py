"""
Схемы данных для регистрации пользователей.

Содержит классы данных, которые помещаются в поле `data` ответов API.
Эти схемы описывают структуру полезной нагрузки ответов регистрации.
"""
from typing import Optional
from datetime import datetime
from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseCommonResponseSchema

class RegistrationDataSchema(BaseCommonResponseSchema):
    """
    Схема данных пользователя при успешной регистрации.

    Содержит основную информацию о зарегистрированном пользователе,
    которая безопасна для передачи клиенту. Исключает конфиденциальные
    данные такие как хешированный пароль.

    Attributes:
        user_id (int): Уникальный идентификатор пользователя в системе
        username (str): Имя пользователя для входа в систему
        email (EmailStr): Email адрес пользователя
        role (str): Роль пользователя в системе (по умолчанию "user")
        is_active (bool): Статус активности аккаунта
        is_verified (bool): Статус верификации email/телефона
        created_at (datetime): Дата и время создания аккаунта
        referral_code (str | None): Реферальный код пользователя (если есть)

    Example:
        ```python
        {
            "user_id": 123,
            "username": "john_doe",
            "email": "john@example.com",
            "role": "user",
            "is_active": True,
            "is_verified": False,
            "created_at": "2024-01-15T10:30:00Z",
            "referral_code": "REF123ABC"
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

class VerificationDataSchema(BaseCommonResponseSchema):
    """
    Данные верификации email адреса.

    Содержит информацию о результате подтверждения email.
    Возвращается после успешной верификации по токену.

    Attributes:
        user_id (int): ID пользователя
        message (str): Сообщение об успешной верификации
        access_token (Optional[str]): Новый JWT токен доступа
        refresh_token (Optional[str]): Новый JWT токен для обновления
        token_type (str): Тип токена
        verified_at (Optional[datetime]): Время верификации
    """
    user_id: int = Field(
        description="Идентификатор верифицированного пользователя",
        example=123
    )
    access_token: Optional[str] = Field(
        default=None,
        description="Новый полный JWT токен доступа"
    )

    refresh_token: Optional[str] = Field(
        default=None,
        description="Новый JWT токен для обновления"
    )

    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )

    verified_at: datetime = Field(
        description="Время подтверждения email в формате UTC",
        example="2024-01-15T10:35:00Z"
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
        description="Email адрес для повторной отправки",
        example="john@example.com"
    )
    sent_at: datetime = Field(
        description="Время отправки письма в формате UTC",
        example="2024-01-15T10:40:00Z"
    )
    expires_in: int = Field(
        description="Время действия токена верификации в секундах",
        example=3600
    )
