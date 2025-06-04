from typing import TYPE_CHECKING, List, Optional

from pydantic import Field

from app.schemas import BaseSchema

if TYPE_CHECKING:
    pass


class CategoryResponseSchema(BaseSchema):
    """
    Схема ответа для категории товаров.
    Содержит информацию о названии и описании категории.

    Attributes:
        id (int): Уникальный идентификатор категории.
        title (str): Название категории.
        description (Optional[str]): Описание категории (необязательное поле).
    """

    id: int
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
    parent: Optional["CategoryShortResponseSchema"] = Field(
        default=None, description="Родительская категория (если есть)"
    )
    children: Optional[List["CategoryShortResponseSchema"]] = Field(
        default=None, description="Дочерние категории (если есть)"
    )


class CategoryShortResponseSchema(BaseSchema):
    """
    Схема ответа для краткой информации о категории товаров.
    Содержит только идентификатор и название категории.

    Attributes:
        id (int): Уникальный идентификатор категории.
        title (str): Название категории.
    """

    id: int
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
