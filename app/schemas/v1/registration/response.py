"""
Схемы ответов для регистрации пользователей.

Модуль содержит Pydantic схемы для структурирования ответов API при регистрации
новых пользователей. Обеспечивает единообразный формат возвращаемых данных
и соответствует архитектуре базовых схем приложения.

Схемы:
    - RegistrationDataSchema: Данные пользователя в ответе регистрации
    - RegistrationResponseSchema: Полная схема ответа API при регистрации
"""
from typing import Optional

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
        access_token (Optional[str]): JWT токен доступа (ограниченный до верификации email)
        refresh_token (Optional[str]): JWT токен для обновления access токена
        token_type (str): Тип токена
        requires_verification (bool): Требуется ли верификация email для полного доступа


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
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "requires_verification": True
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
    )

    access_token: Optional[str] = Field(
        default=None,
        description="JWT токен доступа (ограниченный до верификации email)"
    )

    refresh_token: Optional[str] = Field(
        default=None,
        description="JWT токен для обновления access токена"
    )

    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )

    requires_verification: bool = Field(
        default=True,
        description="Требуется ли верификация email для полного доступа"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Регистрация успешно завершена. Подтвердите email для полного доступа.",
                "item": {
                    "user_id": 123,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "role": "user",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2024-01-15T10:30:00Z",
                    "referral_code": "REF12345678"
                },
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "requires_verification": True
            }
        }


class VerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешной верификации email

    Attributes:
        user_id (int): ID пользователя
        message (str): Сообщение об успешной верификации
        access_token (Optional[str]): Новый JWT токен доступа
        refresh_token (Optional[str]): Новый JWT токен для обновления
        token_type (str): Тип токена
        # verified_at (Optional[datetime]): Время верификации (пока закомментировано, не используется)
    """

    user_id: int = Field(description="ID верифицированного пользователя")

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

    # !Пока оставим закомментированным, по месту не используется.
    # verified_at: Optional[datetime] = Field(
    #     default=None,
    #     description="Время верификации"
    # )


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
