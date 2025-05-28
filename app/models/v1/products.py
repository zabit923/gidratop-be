from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models.v1.carts import CartItem
    from app.models.v1.categories import SubCategory


class Product(BaseModel):
    """
    Модель продукта в системе.
    Содержит информацию о товаре, его характеристиках,
    ценах и доступности.
    Attributes:
        title: Название продукта.
        description: Описание продукта.
        brand: Бренд продукта.
        country: Страна производства продукта.
        width: Ширина продукта в сантиметрах.
        height: Высота продукта в сантиметрах.
        category_id: ID категории, к которой принадлежит продукт.
        price: Цена продукта.
        quantity: Количество на складе.
        image: URL изображения продукта.
    """

    __tablename__ = "products"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("sub_categories.id", ondelete="SET NULL"), nullable=True
    )
    brand: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=True)
    width: Mapped[float] = mapped_column(Numeric(8, 2), nullable=True, doc="Ширина, см")
    height: Mapped[float] = mapped_column(
        Numeric(8, 2), nullable=True, doc="Высота, см"
    )
    material: Mapped[str] = mapped_column(nullable=True, doc="Материал")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)
    image: Mapped[str] = mapped_column(nullable=True)

    category: Mapped["SubCategory"] = relationship(
        "SubCategory", back_populates="products"
    )
    items: Mapped["CartItem"] = relationship("CartItem", back_populates="product")


# TODO расширить характеристики продукта
