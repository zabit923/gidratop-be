from typing import TYPE_CHECKING, List, Optional

from pydantic import Field

from app.schemas import BaseSchema

if TYPE_CHECKING:
    from app.schemas.v1 import ProductDataSchema


class CategoryDataSchema(BaseSchema):
    """
    Базовая схема для категорий товаров.
    Содержит общие поля, которые могут быть использованы в других схемах категорий.

    Attributes:
        id: Уникальный идентификатор категории.
        title: Название категории.
        description: Описание категории.
        created_at: Дата и время создания категории.
        updated_at: Дата и время последнего обновления категории.
    """

    title: str = Field(
        description="Название категории", examples=["Электроника", "Одежда", "Книги"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание категории",
        examples=[
            "Все виды электроники",
            "Одежда для мужчин и женщин",
            "Книги разных жанров",
        ],
    )
    parent: Optional["CategoryDataSchema"]
    children: Optional[List["CategoryDataSchema"]]
    products: Optional[List["ProductDataSchema"]]
