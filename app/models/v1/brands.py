from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models.v1.products import Product


class Brand(BaseModel):
    """
    Модель бренда в системе.
    Содержит информацию о бренде и его продуктах.
    Attributes:
        title: Название бренда.
        products: Список продуктов, связанных с этим брендом.
    """

    __tablename__ = "brands"

    title: Mapped[str] = mapped_column(nullable=False, unique=True)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand")
