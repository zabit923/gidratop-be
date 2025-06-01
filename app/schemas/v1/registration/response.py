"""
Схемы ответов для регистрации пользователей.

Содержит Pydantic схемы для исходящих данных endpoints регистрации.
Все схемы следуют единому формату: {success, message, data}.
"""

from pydantic import EmailStr

from app.schemas.v1.base import (BaseResponseSchema, ItemResponseSchema)
from .base import (
    RegistrationDataSchema,
    VerificationDataSchema,
    ResendVerificationDataSchema
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

    data: RegistrationDataSchema


class VerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при успешной верификации email.

    Возвращается после подтверждения email адреса по токену из письма.
    Подтверждает активацию аккаунта и возможность входа в систему.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате верификации
        data: Данные о верификации

    Example:
        {
            "success": true,
            "message": "Email успешно подтвержден. Теперь вы можете войти в систему",
            "data": {
                "user_id": 123,
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "verified_at": "2024-01-15T10:35:00Z",
            }
        }
    """
    data: VerificationDataSchema


class ResendVerificationResponseSchema(BaseResponseSchema):
    """
    Схема ответа при повторной отправке письма верификации.

    Возвращается при запросе на повторную отправку токена подтверждения email.
    Содержит информацию о новом письме и времени его действия.

    Attributes:
        success: Статус успешности операции (всегда True)
        message: Сообщение о результате отправки
        data: Данные о повторной отправке

    Example:
        {
            "success": true,
            "message": "Письмо верификации отправлено повторно",
            "data": {
                "email": "john@example.com",
                "sent_at": "2024-01-15T10:40:00Z",
                "expires_in": 3600
            }
        }
    """
    data: ResendVerificationDataSchema


class VerificationStatusResponseSchema(BaseResponseSchema):
    """
    Схема ответа о статусе верификации email !TODO: сделать с data

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
