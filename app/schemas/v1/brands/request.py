from typing import Optional

from app.schemas import BaseRequestSchema


class BrandCreateSchema(BaseRequestSchema):
    """
    Схема запроса для создания бренда.

    Attributes:
        title: Название бренда.
    """

    title: str


class BrandUpdateSchema(BaseRequestSchema):
    """
    Схема запроса для обновления бренда.

    Attributes:
        title: Название бренда.
    """

    title: Optional[str]
