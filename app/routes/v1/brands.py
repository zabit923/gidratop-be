from typing import Optional

from fastapi import Depends, File, Form, UploadFile
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session
from app.core.integrations.storage import BrandS3DataManager, get_brand_s3_manager
from app.core.security.auth import get_current_user
from app.models import UserModel
from app.routes.base import BaseRouter
from app.schemas import (
    BrandCreateSchema,
    BrandListResponseSchema,
    BrandResponseSchema,
    BrandUpdateSchema,
    Page,
    PaginationParams,
)
from app.services.v1.brands.service import BrandService


class BrandRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="brands", tags=["Brands"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=BrandResponseSchema,
            status_code=status.HTTP_201_CREATED,
            summary="Создание нового бренда",
        )
        async def create_brand(
            new_brand: BrandCreateSchema,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> BrandResponseSchema:
            return await BrandService(session).create_brand(user, new_brand)

        @self.router.get(
            path="",
            response_model=BrandListResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Получение всех брендов",
        )
        async def get_all_brands(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            search: Optional[str] = Query(None, description="Поиск по данным бренда"),
            session: AsyncSession = Depends(get_db_session),
        ) -> BrandListResponseSchema:
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **search**: Строка поиска по данным бренда
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            brands, total = await BrandService(session).get_all_brands(
                pagination=pagination,
                search=search,
            )
            page = Page(
                items=brands,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return BrandListResponseSchema(data=page)

        @self.router.patch(
            path="/{brand_id}",
            response_model=BrandResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Обновление бренда",
        )
        async def update_brand(
            brand_id: int,
            title: Optional[str] = Form(None),
            image: Optional[UploadFile] = File(None),
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
            s3_data_manager: BrandS3DataManager = Depends(get_brand_s3_manager),
        ) -> BrandResponseSchema:
            brand_data = BrandUpdateSchema(title=title)
            return await BrandService(session, s3_data_manager).update_brand(
                user, brand_id, brand_data, image
            )

        @self.router.delete(
            path="/{brand_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удаление бренда по ID",
        )
        async def delete_brand(
            brand_id: int,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> None:
            await BrandService(session).delete_brand(user, brand_id)
