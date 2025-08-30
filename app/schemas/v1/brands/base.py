from pydantic import Field

from app.schemas import BaseSchema


class BrandDataSchema(BaseSchema):
    """
    Схема данных бренда.

    Attributes:
        title: Название бренда.
    """

    title: str = Field(description="Название бренда.")
