"""
Схемы ответов для регистрации пользователей.

Модуль содержит Pydantic схемы для структурирования ответов API при регистрации
новых пользователей. Обеспечивает единообразный формат возвращаемых данных
и соответствует архитектуре базовых схем приложения.

Схемы:
    - RegistrationDataSchema: Данные пользователя в ответе регистрации
    - RegistrationResponseSchema: Полная схема ответа API при регистрации
"""

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.v1.base import (BaseCommonResponseSchema, BaseResponseSchema,
                                 ItemResponseSchema)


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


class RegistrationResponseSchema(ItemResponseSchema[RegistrationDataSchema]):
    """
    Схема полного ответа API при успешной регистрации пользователя.

    Наследуется от ItemResponseSchema и содержит стандартные поля ответа
    (success, message) плюс данные зарегистрированного пользователя.
    Обеспечивает единообразный формат ответов во всем API.

    Attributes:
        success (bool): Статус успешности операции (наследуется, всегда True)
        message (str): Информационное сообщение о результате регистрации
        item (RegistrationDataSchema): Данные зарегистрированного пользователя

    Example:
        ```python
        {
            "success": true,
            "message": "Регистрация успешно завершена",
            "item": {
                "user_id": 123,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "user",
                "is_active": true,
                "is_verified": false,
                "created_at": "2024-01-15T10:30:00Z",
                "referral_code": "REF123ABC"
            }
        }
        ```

    Usage:
        ```python
        @router.post("/register", response_model=RegistrationResponseSchema)
        async def register_user(user_data: RegistrationRequestSchema):
            # Логика регистрации
            return RegistrationResponseSchema(
                message="Регистрация успешно завершена",
                item=registration_data
            )
        ```
    """

    message: str = Field(
        default="Регистрация успешно завершена",
        description="Сообщение о результате операции регистрации",
        examples=[
            "Регистрация успешно завершена",
            "Пользователь создан, проверьте email для активации",
            "Аккаунт создан успешно",
        ],
    )


class VerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешной верификации email

    Attributes:
        user_id (int): ID пользователя
        message (str): Сообщение об успешной верификации
    """

    user_id: int
    message: str = "Email успешно подтвержден"


class ResendVerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа на запрос повторной отправки письма верификации

    Attributes:
        email (EmailStr): Email пользователя
        message (str): Сообщение о результате операции
    """

    email: EmailStr
    message: str = "Письмо для подтверждения email отправлено"


class VerificationStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа о статусе верификации email

    Attributes:
        email (EmailStr): Email пользователя
        is_verified (bool): Статус верификации
        message (str): Сообщение о статусе верификации
    """

    email: EmailStr
    is_verified: bool
    message: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        self.message = (
            "Email подтвержден" if self.is_verified else "Email не подтвержден"
        )
