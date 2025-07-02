from typing import Optional

from app.schemas import BaseRequestSchema


class CardCreateSchema(BaseRequestSchema):
    """
    Схема запроса для создания карточки.

    Attributes:
        title: Название карточки.
    """

    title: str


class CardUpdateSchema(BaseRequestSchema):
    """
    Схема запроса для обновления карточки.

    Attributes:
        title: Название карточки.
    """

    title: Optional[str]
