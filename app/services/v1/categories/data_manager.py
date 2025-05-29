# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.models import Category
# from app.schemas import CategoryDataSchema
# from app.services.v1.base import BaseEntityManager
#
#
# class CategoryDataManager(BaseEntityManager[CategoryDataSchema]):
#     """
#     Менеджер данных для работы с категориями товаров.
#     Реализует низкоуровневые операции для работы с таблицами категорий в БД.
#     Обрабатывает исключения БД и преобразует их в доменные исключения.
#
#     Attributes:
#         session (AsyncSession): Асинхронная сессия БД
#         schema (Type[CategorySchema]): Схема сериализации данных
#         model (Type[CategoryModel]): Модель категории товаров
#
#     Methods:
#         add_category: Добавление новой категории в БД
#     """
#
#     def __init__(self, session: AsyncSession):
#         super().__init__(session=session, schema=CategoryDataSchema, model=Category)
#
#     def add_category(self, category: Category) -> Category:
#         return self.add_one(category)
