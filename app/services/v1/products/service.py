from typing import List, Optional, Tuple

from app.core.exceptions import CategoryNotFoundError, ForbiddenError
from app.models import Product, UserModel
from app.schemas import PaginationParams, ProductCreateSchema, ProductResponseSchema
from app.services.v1.base import BaseService
from app.services.v1.categories.data_manager import CategoryDataManager
from app.services.v1.products.data_manager import ProductDataManager


class ProductService(BaseService):
    """
    Сервис для работы с продуктами.

    Atributes:
        session (AsyncSession): Асинхронная сессия для работы с базой данных
        data_manager (ProductDataManager): Менеджер данных для операций с продуктами

    Methods:
        get_all_products: Получает все продукты с пагинацией и фильтрацией
        get_product_by_id: Получает продукт по ID
        create_product: Создает новый продукт
        update_product: Обновляет существующий продукт
        delete_product: Удаляет продукт по ID
    """

    def __init__(self, session):
        super().__init__(session)
        self.data_manager = ProductDataManager(session)
        self.category_data_manager = CategoryDataManager(session)

    async def get_all_products(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Tuple[List[ProductResponseSchema], int]:
        products, total = await self.data_manager.get_all_products(
            pagination, search, category_id
        )
        return [
            ProductResponseSchema.model_validate(product) for product in products
        ], total

    async def create_product(
        self, user: UserModel, data: ProductCreateSchema
    ) -> Product:
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для создания продукта",
                required_role="MODERATOR",
            )
        if data.category_id is not None:
            category = await self.category_data_manager.get_category_by_id(
                data.category_id
            )
            if not category:
                raise CategoryNotFoundError(
                    field="id", value=data.category_id, detail="Категория не найдена"
                )
        return await self.data_manager.add_product(data)
