from typing import List, Optional

from pydantic import Field

from app.schemas import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page


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


class CategoryListResponseSchema(BaseResponseSchema):
    """
    Схема ответа для списка категорий товаров.
    Содержит общее количество категорий и список категорий.

    Attributes:
        message (str): Сообщение о результате операции
        data (Page[CategoryResponseSchema]): Список пользователей
    """

    message: str = "Список категорий успешно получен"
    data: Page[CategoryShortResponseSchema]


class CategoryDeleteResponseSchema(BaseResponseSchema):
    """
    Схема ответа для удаления категории товаров.
    Содержит сообщение об успешном удалении категории.

    Attributes:
        message (str): Сообщение о результате операции
    """

    message: str = "Категория успешно удалена"
