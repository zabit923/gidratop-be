from typing import List, Optional

from botocore.exceptions import ClientError
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BrandAlreadyExistsError,
    BrandNotFoundError,
    InvalidFileTypeError,
    StorageError,
)
from app.core.exceptions.users import ForbiddenError
from app.core.integrations.storage import BrandS3DataManager
from app.models import Brand, UserModel
from app.schemas import (
    BrandCreateSchema,
    BrandResponseSchema,
    BrandUpdateSchema,
    CategoryResponseSchema,
    PaginationParams,
)
from app.services.v1.base import BaseService
from app.services.v1.brands.data_manager import BrandDataManager


class BrandService(BaseService):
    """
    Сервис для работы с брендами.

    Atributes:
        session (AsyncSession): Асинхронная сессия для работы с базой данных
        data_manager (BrandDataManager): Менеджер данных для операций с брендами

    Methods:
        get_all_brands: Получает все бренды
        create_brand: Создает новый бренд
        update_brand: Обновляет существующий бренд
        delete_brand: Удаляет бренд по ID
    """

    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[BrandS3DataManager] = None,
    ):
        super().__init__(session)
        self.data_manager = BrandDataManager(session)
        self.s3_data_manager = s3_data_manager

    async def create_brand(
        self, user: UserModel, data: BrandCreateSchema
    ) -> BrandResponseSchema:
        existing_brand = await self.data_manager.get_model_by_field("title", data.title)
        if existing_brand:
            raise BrandAlreadyExistsError(
                field="title",
                value=data.title,
                detail="Бренд с таким названием уже существует",
            )
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для создания бренда",
                required_role="MODERATOR",
            )
        brand = await self.data_manager.add_brand(data)
        return CategoryResponseSchema.model_validate(brand)

    async def update_brand(
        self,
        user: UserModel,
        brand_id: int,
        data: BrandUpdateSchema,
        image: Optional[UploadFile] = None,
    ) -> BrandResponseSchema:
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для обновления бренда",
                required_role="MODERATOR",
            )
        brand = await self.data_manager.get_model_by_field("id", brand_id)
        if not brand:
            raise BrandNotFoundError(
                field="id", value=brand_id, detail="Бренд не найдена"
            )
        if data.title:
            existing_brand = await self.data_manager.get_model_by_field(
                "title", data.title
            )
            if existing_brand and existing_brand.id != brand_id:
                raise BrandAlreadyExistsError(
                    field="title",
                    value=data.title,
                    detail="Бренд с таким названием уже существует",
                )
        if image:
            await self._update_brand_image(brand, image)
        updated_brand = await self.data_manager.update_brand(brand, data)
        serialized_brand = await self.data_manager.get_brand_by_id(updated_brand.id)
        return BrandResponseSchema.model_validate(serialized_brand)

    async def _update_brand_image(
        self,
        brand: Brand,
        file: UploadFile,
    ) -> None:
        file_content = await file.read()
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidFileTypeError()
        old_image_url = None
        if hasattr(brand, "image") and brand.image:
            old_image_url = brand.image
            self.logger.info("Текущее изображение: %s", old_image_url)
        else:
            self.logger.info("Изображение не установлено")
        try:
            image_url = await self.s3_data_manager.process_brand_image(
                old_image_url=old_image_url if old_image_url else "",
                file=file,
                file_content=file_content,
            )
            self.logger.info("Файл загружен: %s", image_url)
        except ClientError as e:
            self.logger.error("Ошибка S3 при загрузке изображения: %s", str(e))
            raise StorageError(detail=f"Ошибка хранилища: {str(e)}")
        except ValueError as e:
            self.logger.error("Ошибка валидации при загрузке изображения: %s", str(e))
            raise StorageError(detail=str(e))
        except Exception as e:
            self.logger.error("Неизвестная ошибка при загрузке изображения: %s", str(e))
            raise StorageError(detail=f"Ошибка при загрузке изображения: {str(e)}")

        await self.data_manager.update_image(brand, image_url)

    async def get_all_brands(
        self,
        pagination: PaginationParams,
        search: str = None,
    ) -> List[BrandResponseSchema]:
        brands, total = await self.data_manager.get_all_brands(
            pagination=pagination,
            search=search,
        )
        return [BrandResponseSchema.model_validate(brand) for brand in brands], total

    async def delete_brand(self, user: UserModel, brand_id: int) -> None:
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для обновления бренда",
                required_role="MODERATOR",
            )
        brand = await self.data_manager.get_brand_by_id(brand_id)
        if not brand:
            raise BrandNotFoundError(
                field="id", value=brand_id, detail="Бренд не найден"
            )
        await self.data_manager.delete_item(brand_id)
