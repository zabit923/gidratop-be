from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CartItem
from app.schemas import CartItemDataSchema
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
