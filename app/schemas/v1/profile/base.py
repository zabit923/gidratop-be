from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseSchema


class ProfileSchema(BaseSchema):
    """
    Схема для представления профиля пользователя.

    Args:
        username: Имя пользователя.
        email: Электронная почта пользователя.
        phone: Телефон пользователя.
        avatar: URL аватара пользователя.
    """

    username: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(description="Email пользователя")
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
