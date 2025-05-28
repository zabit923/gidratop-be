from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models.v1.products import Product


class MainCategory(BaseModel):
    """
    Модель категории товаров.
    Содержит информацию о названии и описании категории.

    Attributes:
        title: Название категории.
        description: Описание категории.
    """

    __tablename__ = "main_categories"

    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=True)

    sub_category: Mapped[List["SubCategory"]] = relationship(
        "SubCategory", back_populates="main_category"
    )


class SubCategory(BaseModel):
    """
    Модель подкатегории товаров.
    Содержит информацию о названии, описании и родительской категории.

    Attributes:
        title: Название подкатегории.
        description: Описание подкатегории.
        main_category_id: ID родительской категории.
    """

    __tablename__ = "sub_categories"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    main_category_id: Mapped[int] = mapped_column(
        ForeignKey("main_categories.id", ondelete="CASCADE")
    )

    main_category: Mapped["MainCategory"] = relationship(
        "MainCategory", back_populates="sub_categories"
    )
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="category"
    )
