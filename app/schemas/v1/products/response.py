from typing import List, Optional

from app.schemas import BaseResponseSchema, BaseSchema
from app.schemas.v1.brands import BrandResponseSchema
from app.schemas.v1.categories import CategoryShortResponseSchema
from app.schemas.v1.pagination import Page


class ProductResponseSchema(BaseSchema):
    """
    Схема ответа для продукта.
    Содержит информацию о названии, описании, бренде, стране производства,
    размерах, материале, цене, количестве и категории продукта.

    Attributes:
        id (int): Уникальный идентификатор продукта.
        title (str): Название продукта.
        description (Optional[str]): Описание продукта (необязательное поле).
        country (Optional[str]): Страна производства продукта (необязательное поле).
        width (Optional[float]): Ширина продукта в сантиметрах (необязательное поле).
        height (Optional[float]): Высота продукта в сантиметрах (необязательное поле).
        material (Optional[str]): Материал продукта (необязательное поле).
        price (float): Цена продукта.
        quantity (int): Количество продукта на складе.
        category (Optional[CategoryShortResponseSchema]): Идентификатор категории, к которой принадлежит продукт.
        brand (Optional[BrandResponseSchema]): Бренд продукта.
    """

    id: int
    title: str
    description: Optional[str] = None
    country: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    material: Optional[str] = None
    price: float
    quantity: int
    images: Optional[List[str]] = None
    category: Optional["CategoryShortResponseSchema"] = None
    brand: Optional["BrandResponseSchema"] = None
    discount: Optional[int] = None
    sales_count: Optional[int] = None
    new_arrivals: Optional[bool] = None


class ProductListResponseSchema(BaseResponseSchema):
    """
    Схема ответа для списка продуктов.
    Содержит общее количество продуктов и список продуктов.

    Attributes:
        message (str): Сообщение о результате операции.
        data (Page[ProductResponseSchema]): Список продуктов.
    """

    message: str = "Список продуктов успешно получен"
    data: Page[ProductResponseSchema]


ProductResponseSchema.model_rebuild()
