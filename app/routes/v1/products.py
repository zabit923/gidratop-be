from typing import Optional

from fastapi import Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session
from app.core.security.auth import get_current_user
from app.models import UserModel
from app.routes.base import BaseRouter
from app.schemas import (
    Page,
    PaginationParams,
    ProductCreateSchema,
    ProductListResponseSchema,
    ProductResponseSchema,
)
from app.services.v1.products.service import ProductService


class ProductRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="products", tags=["Products"])

    def configure(self):
        @self.router.post(
            "",
            response_model=ProductResponseSchema,
            status_code=status.HTTP_201_CREATED,
            summary="Создание нового продукта",
        )
        async def create_product(
            new_product: ProductCreateSchema,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> ProductResponseSchema:
            return await ProductService(session).create_product(user, new_product)

        @self.router.get(
            "",
            response_model=ProductListResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Получение списка продуктов",
        )
        async def list_products(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            search: Optional[str] = Query(None, description="Поиск по данным продукта"),
            category_id: Optional[int] = Query(
                None, description="ID категории для фильтрации"
            ),
            session: AsyncSession = Depends(get_db_session),
        ) -> ProductListResponseSchema:
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **search**: Строка поиска по данным продукта
            * **category_id**: ID категории для фильтрации
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            products, total = await ProductService(session).get_all_products(
                pagination=pagination,
                search=search,
                category_id=category_id,
            )
            page = Page(
                items=products,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return ProductListResponseSchema(data=page)
