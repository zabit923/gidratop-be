from typing import Optional

from pydantic import Field

from app.schemas import BaseSchema


class CardDataSchema(BaseSchema):
    """
    Схема данных карточки.

    Attributes:
        title: Название карточки.
        image: Ссылка на изображение карточки.
    """

    title: str = Field(description="Название карточки")
    image: Optional[str] = Field(default=None, description="Изображение карточки")
