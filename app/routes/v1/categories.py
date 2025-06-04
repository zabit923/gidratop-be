from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.connections.database import get_db_session
from app.core.security.auth import get_current_user
from app.models import UserModel
from app.routes.base import BaseRouter
from app.schemas.v1.categories.request import CategoryCreateSchema
from app.schemas.v1.categories.response import CategoryResponseSchema
from app.services.v1.categories.service import CategoryService


class CategoryRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="categories", tags=["Категории"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=CategoryResponseSchema,
            status_code=status.HTTP_201_CREATED,
            summary="Создание новой категории",
        )
        async def create_category(
            new_category: CategoryCreateSchema,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> CategoryResponseSchema:
            return await CategoryService(session).create_category(user, new_category)

        @self.router.get(
            path="",
            response_model=List[CategoryResponseSchema],
            status_code=status.HTTP_200_OK,
            summary="Получение всех категорий",
        )
        async def get_all_categories(
            session: AsyncSession = Depends(get_db_session),
        ) -> List[CategoryResponseSchema]:
            return await CategoryService(session).get_all_categories()

        @self.router.patch(
            path="/{category_id}",
            response_model=CategoryResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Обновление категории",
        )
        async def update_category(
            category_id: int,
            updated_category: CategoryCreateSchema,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> CategoryResponseSchema:
            return await CategoryService(session).update_category(
                user, category_id, updated_category
            )

        @self.router.get(
            path="/{category_id}",
            response_model=CategoryResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Получение категории по ID",
        )
        async def get_category_by_id(
            category_id: int,
            session: AsyncSession = Depends(get_db_session),
        ) -> CategoryResponseSchema:
            return await CategoryService(session).get_category_by_id(category_id)
