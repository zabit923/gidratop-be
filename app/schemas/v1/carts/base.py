from pydantic import Field

from app.schemas import BaseSchema


class CartDataSchema(BaseSchema):
    """
    Схема данных корзины пользователя.

    Attributes:
        user_id (int): ID пользователя, которому принадлежит корзина.
    """

    user_id: int = Field(description="ID пользователя, которому принадлежит корзина.")
