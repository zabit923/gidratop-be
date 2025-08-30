from typing import Optional

from app.schemas import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page


class CardResponseSchema(BaseSchema):
    """
    Схема ответа для карточки.

    Attributes:
        id (int): Уникальный идентификатор карточки
        title (str): Название карточки
        image Optional(str): URL изображения карточки
    """

    title: str
    image: Optional[str] = None


class CardListResponseSchema(BaseResponseSchema):
    """
    Схема ответа для списка карточек.
    Содержит общее количество карточек и список карточек.

    Attributes:
        message (str): Сообщение о результате операции.
        data (Page[CardResponseSchema]): Список карточек.
    """

    message: str = "Список карточек успешно получен"
    data: Page[CardResponseSchema]
