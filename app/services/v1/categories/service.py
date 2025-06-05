from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError
from app.core.exceptions.users import ForbiddenError
from app.models import UserModel
from app.schemas import CategoryCreateSchema, CategoryResponseSchema, PaginationParams
from app.services.v1.base import BaseService
from app.services.v1.categories.data_manager import CategoryDataManager


class CategoryService(BaseService):
    """
    Сервис для работы с основными категориями товаров.

    Atributes:
        session (AsyncSession): Асинхронная сессия для работы с базой данных
        data_manager (CategoryDataManager): Менеджер данных для операций с основными категориями

    Methods:
        get_all_categories: Получает все основные категории товаров
        get_category_by_id: Получает основную категорию по ID
        create_category: Создает новую основную категорию
        update_category: Обновляет существующую основную категорию
        delete__category: Удаляет основную категорию по ID
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.data_manager = CategoryDataManager(session)

    async def create_category(
        self, user: UserModel, data: CategoryCreateSchema
    ) -> CategoryResponseSchema:
        existing_category = await self.data_manager.get_model_by_field(
            "title", data.title
        )
        if existing_category:
            raise CategoryAlreadyExistsError(
                field="title",
                value=data.title,
                detail="Категория с таким названием уже существует",
            )
        if data.parent_id is not None:
            parent = await self.data_manager.get_model_by_field("id", data.parent_id)
            if not parent:
                raise CategoryNotFoundError(
                    field="id",
                    value=data.parent_id,
                    detail="Родительская категория не найдена",
                )
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для создания категории",
                required_role="MODERATOR",
            )
        category = await self.data_manager.add_category(data)
        return CategoryResponseSchema.model_validate(category)

    async def update_category(
        self, user: UserModel, category_id: int, data: CategoryCreateSchema
    ) -> CategoryResponseSchema:
        category = await self.data_manager.get_model_by_field("id", category_id)
        if not category:
            raise CategoryNotFoundError(
                field="id", value=category_id, detail="Категория не найдена"
            )
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для обновления категории",
                required_role="MODERATOR",
            )
        updated_category = await self.data_manager.update_category(category, data)
        return CategoryResponseSchema.model_validate(updated_category)

    async def get_all_categories(
        self,
        pagination: PaginationParams,
        search: str = None,
    ) -> list[CategoryResponseSchema]:
        categories, total = await self.data_manager.get_all_categories(
            pagination=pagination,
            search=search,
        )
        return [CategoryResponseSchema.model_validate(cat) for cat in categories], total

    async def get_category_by_id(self, category_id: int) -> CategoryResponseSchema:
        category = await self.data_manager.get_category_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(
                field="id", value=category_id, detail="Категория не найдена"
            )
        return CategoryResponseSchema.model_validate(category)

    async def delete_category(self, user: UserModel, category_id: int) -> None:
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для обновления категории",
                required_role="MODERATOR",
            )
        category = await self.data_manager.get_category_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(
                field="id", value=category_id, detail="Категория не найдена"
            )
        await self.data_manager.delete_item(category_id)
