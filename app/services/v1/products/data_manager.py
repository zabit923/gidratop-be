from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas import ProductCreateSchema, ProductDataSchema
from app.services.v1.base import BaseEntityManager


class ProductDataManager(BaseEntityManager[ProductDataSchema]):
    """
    Менеджер данных для работы с продуктами.
    Реализует низкоуровневые операции для работы с таблицами продуктов в БД.
    Обрабатывает исключения БД и преобразует их в доменные исключения.
    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[ProductDataSchema]): Схема сериализации данных
        model (Type[Product]): Модель продукта
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=ProductDataManager, model=Product)

    async def get_by_id(self, product_id: int) -> Product:
        statement = select(Product).where(Product.id == product_id)
        return await self.get_one(statement)

    async def add_product(self, data: ProductCreateSchema) -> Product:
        product_model = Product(
            title=data.title,
            description=data.description,
            price=data.price,
            category_id=data.category_id,
            image_url=data.image_url,
        )
        return await self.add_one(product_model)
