from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Cart, CartItem, Product
from app.schemas import CartItemCreateSchema, CartItemDataSchema
from app.services.v1.base import BaseEntityManager


class CartItemDataManager(BaseEntityManager[CartItemDataSchema]):
    """
    Менеджер данных для работы с элементами корзины.
    Реализует низкоуровневые операции для работы с таблицами элементов корзины в БД.
    Обрабатывает исключения БД и преобразует их в доменные исключения.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[CartItemDataSchema]): Схема сериализации данных
        model (Type[CartItem]): Модель элемента корзины
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=CartItemDataSchema, model=CartItem)

    async def add_cart_item(
        self, product: Product, cart: Cart, data: CartItemCreateSchema
    ) -> CartItem:
        cart_item_model = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=data.quantity,
        )
        return await self.add_one(cart_item_model)

    async def get_cart_items(self, cart_id: int):
        query = (
            select(CartItem)
            .options(joinedload(CartItem.product).joinedload(Product.category))
            .where(CartItem.cart_id == cart_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
