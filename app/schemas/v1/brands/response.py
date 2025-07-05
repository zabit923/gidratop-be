from typing import Optional

from app.schemas import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page


class BrandResponseSchema(BaseSchema):
    """
    Схема ответа для бренда.

    Attributes:
        id (int): Уникальный идентификатор бренда
        title (str): Название бренда
        image Optional(str): URL изображения бренда
    """

    title: str
    image: Optional[str] = None


class BrandListResponseSchema(BaseResponseSchema):
    """
    Схема ответа для списка брендов.
    Содержит общее количество брендов и список брендов.

    Attributes:
        message (str): Сообщение о результате операции.
        data (Page[BrandResponseSchema]): Список брендов.
    """

    message: str = "Список брендов успешно получен"
    data: Page[BrandResponseSchema]
