# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.schemas.v1.categories.base import CategoryDataSchema
# from app.services.v1.base import BaseService
# from app.services.v1.categories.data_manager import CategoryDataManager
#
#
# class CategoryService(BaseService):
#     """
#     Сервис для работы с основными категориями товаров.
#
#     Atributes:
#         session (AsyncSession): Асинхронная сессия для работы с базой данных
#         data_manager (CategoryDataManager): Менеджер данных для операций с основными категориями
#
#     Methods:
#         get_all_categories: Получает все основные категории товаров
#         get_category_by_id: Получает основную категорию по ID
#         create_category: Создает новую основную категорию
#         update_category: Обновляет существующую основную категорию
#         delete__category: Удаляет основную категорию по ID
#     """
#
#     def __init__(self, session: AsyncSession):
#         super().__init__(session)
#         self.data_manager = CategoryDataManager(session)
#
#     async def add_category(self, data: CategoryDataSchema) -> MainCategoryResponseSchema:
#
