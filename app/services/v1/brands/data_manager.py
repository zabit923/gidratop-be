from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Brand
from app.schemas import (
    BrandCreateSchema,
    BrandDataSchema,
    BrandUpdateSchema,
    PaginationParams,
)
from app.services.v1.base import BaseEntityManager


class BrandDataManager(BaseEntityManager[BrandDataSchema]):
    """
    Менеджер данных для работы с брендами.
    Реализует низкоуровневые операции для работы с таблицами категорий в БД.
    Обрабатывает исключения БД и преобразует их в доменные исключения.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[BrandSchema]): Схема сериализации данных
        model (Type[Brand]): Модель брендов
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=BrandDataSchema, model=Brand)

    async def add_brand(self, data: BrandCreateSchema) -> Brand:
        brand_model = Brand(title=data.title)
        return await self.add_one(brand_model)

    async def update_brand(self, brand: Brand, data: BrandUpdateSchema) -> Brand:
        brand_data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in brand_data_dict.items():
            setattr(brand, key, value)
        return await self.update_one(brand)

    async def update_image(self, brand: Brand, image_url: str) -> None:
        try:
            await self.update_items(brand.id, {"image": image_url})
        except (ValueError, SQLAlchemyError):
            self.logger.error("Не удалось обновить изображение для бренда %s", brand.id)
            raise RuntimeError(f"Не удалось обновить изображение для бренда {brand.id}")

    async def get_all_brands(
        self,
        pagination: PaginationParams,
        search: str = None,
    ) -> List[Brand]:
        statement = select(Brand)
        if search:
            statement = statement.filter(self.model.title.ilike(f"%{search}%"))
        return await self.get_paginated_items(statement, pagination)

    async def get_brand_by_id(self, brand_id: int) -> Brand:
        statement = select(Brand).where(Brand.id == brand_id)
        return await self.get_one(statement)
