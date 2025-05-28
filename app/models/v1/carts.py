from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import UserModel
    from app.models.v1.products import Product


class Cart(BaseModel):
    """
    Модель корзины пользователя.
    """

    __tablename__ = "carts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[user_id], back_populates="cart"
    )


class CartItem(BaseModel):
    """
    Модель элемента корзины.
    Attributes:
        cart_id (int): ID корзины.
        product_id (int): ID продукта.
        quantity (int): Количество продукта в корзине.
    """

    __tablename__ = "cart_items"

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    cart: Mapped["Cart"] = relationship(
        "CartModel", foreign_keys=[cart_id], back_populates="items"
    )
    product: Mapped["Product"] = relationship(
        "ProductModel", foreign_keys=[product_id], back_populates="items"
    )

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="unique_cart_product"),
    )
