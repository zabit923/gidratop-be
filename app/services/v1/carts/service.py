from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import OutOfStockError, ProductNotFoundError
from app.models import UserModel
from app.schemas import CartItemCreateSchema, ProductResponseSchema
from app.services.v1.base import BaseService
from app.services.v1.cart_items.data_manager import CartItemDataManager
from app.services.v1.carts.data_manager import CartDataManager
from app.services.v1.products.data_manager import ProductDataManager


class CartService(BaseService):
    """
    Сервис для работы с корзинами.
    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с базой данных.
        cart_data_manager (CartDataManager): Менеджер данных для операций с корзинами.
        cart_item_data_manager (CartItemDataManager): Менеджер данных для операций с товарами в корзине.
        product_data_manager (ProductDataManager): Менеджер данных для операций с продуктами.

    Methods:
        get_cart_by_user_id: Получает корзину по ID пользователя.
        create_cart: Создает новую корзину для пользователя.
        add_product_to_cart: Добавляет продукт в корзину.
        remove_product_from_cart: Удаляет продукт из корзины.
        update_product_quantity: Обновляет количество товара в корзине.
        clear_cart: Очищает корзину пользователя.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.cart_data_manager = CartDataManager(session)
        self.cart_item_data_manager = CartItemDataManager(session)
        self.product_data_manager = ProductDataManager(session)

    async def add_product_to_cart(
        self, user: UserModel, data: CartItemCreateSchema
    ) -> ProductResponseSchema:
        product = await self.product_data_manager.get_by_id(data.product_id)
        if not product:
            raise ProductNotFoundError(
                field="id", value=data.product_id, detail="Продукт не найден"
            )
        if data.quantity > product.quantity:
            raise OutOfStockError(
                detail="Недостаточно товара на складе",
                product_id=data.product_id,
                available_quantity=product.quantity,
            )
        cart, _ = await self.cart_data_manager.get_or_create(
            {"user_id": user.id}, {"user_id": user.id}
        )
        await self.cart_item_data_manager.add_cart_item(
            product=product, cart=cart, data=data
        )
        return ProductResponseSchema.model_validate(product)
