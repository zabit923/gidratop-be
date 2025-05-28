"""
Схемы запросов для аутентификации.

Содержит Pydantic схемы для входящих данных в endpoints аутентификации.
"""

from pydantic import EmailStr, Field, field_validator

from app.schemas.v1.base import BaseRequestSchema

class AuthSchema(BaseRequestSchema):
    """
    Схема аутентификации пользователя.

    Attributes:
        username: Идентификатор пользователя (имя, email или телефон)
        password: Пароль пользователя
    """

    username: str = Field(
        description="Имя пользователя, email или телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["user@example.com", "john_doe", "+7 999 123-45-67"]
    )
    password: str = Field(
        description="Пароль (минимум 8 символов, заглавная и строчная буква, цифра, спецсимвол",
    )

class ForgotPasswordSchema(BaseRequestSchema):
    """
    Схема для запроса сброса пароля.

    Attributes:
        email: Email адрес для отправки ссылки восстановления
    """

    email: EmailStr = Field(description="Email адрес для восстановления пароля")


class PasswordResetConfirmSchema(BaseRequestSchema):
    """
    Схема для подтверждения сброса пароля.

    Attributes:
        token: Токен восстановления из email ссылки
        new_password: Новый пароль пользователя
        confirm_password: Подтверждение нового пароля
    """

    token: str = Field(description="Токен восстановления пароля")
    new_password: str = Field(
        description="Новый пароль",
        min_length=8,
        max_length=128
    )
    confirm_password: str = Field(
        description="Подтверждение нового пароля",
        min_length=8,
        max_length=128
    )

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, values):
        """Проверка совпадения паролей"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Пароли не совпадают')
        return v
