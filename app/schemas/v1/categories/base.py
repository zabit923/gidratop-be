from typing import TYPE_CHECKING, Optional

from pydantic import Field

from app.schemas import BaseSchema

if TYPE_CHECKING:
    pass


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
    parent_id: Optional[int] = Field(
        default=None,
        description="ID родительской категории",
        examples=[1, 2, None],
    )
