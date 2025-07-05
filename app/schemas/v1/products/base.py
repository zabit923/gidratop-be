from typing import Optional

from pydantic import Field

from app.schemas.v1.base import BaseSchema
from app.schemas.v1.brands import BrandResponseSchema
from app.schemas.v1.categories import CategoryShortResponseSchema


class ProductDataSchema(BaseSchema):
    """
    Базовая схема для продуктов.
    Содержит общие поля, которые могут быть использованы в других схемах продуктов.

    Attributes:
        title: Название продукта.
        description: Описание продукта.
        price: Цена продукта.
        country: Страна производства продукта.
        width: Ширина продукта в сантиметрах.
        height: Высота продукта в сантиметрах.
        material: Материал продукта.
        quantity: Количество продукта на складе.
        sales_count: Количество проданных товаров.
        discount: Скидка на товар в процентах.
        new_arrivals: Является ли товар новинкой.
    """

    title: str = Field(
        description="Название продукта", examples=["Ноутбук", "Смартфон", "Книга"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание продукта",
        examples=[
            "Мощный ноутбук с 16 ГБ ОЗУ",
            "Смартфон с отличной камерой",
            "Интересная книга по программированию",
        ],
    )
    price: float = Field(description="Цена продукта", examples=[999.99, 499.99, 19.99])
    country: Optional[str] = Field(
        default=None,
        description="Страна производства продукта",
        examples=["США", "Корея", "Япония"],
    )
    width: Optional[float] = Field(
        default=None,
        description="Ширина продукта в сантиметрах",
        examples=[30.5, 15.0, 20.0],
    )
    height: Optional[float] = Field(
        default=None,
        description="Высота продукта в сантиметрах",
        examples=[20.0, 10.0, 5.0],
    )
    material: Optional[str] = Field(
        default=None,
        description="Материал продукта",
        examples=["Пластик", "Металл", "Дерево"],
    )
    quantity: int = Field(
        default=0, description="Количество продукта на складе", examples=[100, 50, 0]
    )
    sales_count: Optional[int] = Field(
        default=0,
        description="Количество проданных товаров",
        examples=[10, 25, 0],
    )
    discount: Optional[int] = Field(
        default=0,
        description="Скидка на товар в процентах",
        examples=[10, 20, 0],
    )
    new_arrivals: Optional[bool] = Field(
        default=False,
        description="Является ли товар новинкой",
        examples=[True, False],
    )
    category: Optional["CategoryShortResponseSchema"] = None
    brand: Optional["BrandResponseSchema"] = None


ProductDataSchema.model_rebuild()
