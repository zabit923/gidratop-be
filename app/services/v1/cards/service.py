from typing import List, Optional

from botocore.exceptions import ClientError
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CardAlreadyExistsError,
    CardNotFoundError,
    ForbiddenError,
    InvalidFileTypeError,
    StorageError,
)
from app.core.integrations.storage import CardS3DataManager
from app.models import Card, UserModel
from app.schemas import (
    CardCreateSchema,
    CardResponseSchema,
    CardUpdateSchema,
    PaginationParams,
)
from app.services.v1.base import BaseService
from app.services.v1.cards.data_manager import CardDataManager


class CardService(BaseService):
    """
    Сервис для работы с карточками.

    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с базой данных
        data_manager (CardDataManager): Менеджер данных для работы с карточками

    Methods:
        get_all_cards: Получает все карточки с возможностью пагинации
        get_card_by_id: Получает карточку по ID
        create_card: Создает новую карточку
        update_card: Обновляет существующую карточку
        delete_card: Удаляет карточку по ID
    """

    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[CardS3DataManager] = None,
    ):
        super().__init__(session)
        self.data_manager = CardDataManager(session)
        self.s3_data_manager = s3_data_manager

    async def create_card(
        self, user: UserModel, data: CardCreateSchema
    ) -> CardResponseSchema:
        existing_card = await self.data_manager.get_model_by_field("title", data.title)
        if existing_card:
            raise CardAlreadyExistsError(
                field="title",
                value=data.title,
                detail="Карточка с таким названием уже существует",
            )
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для создания карточки",
                required_role="MODERATOR",
            )
        card = await self.data_manager.add_card(data)
        return CardResponseSchema.model_validate(card)

    async def update_card(
        self,
        user: UserModel,
        card_id: int,
        data: CardUpdateSchema,
        image: Optional[UploadFile] = None,
    ) -> CardResponseSchema:
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для обновления карточки",
                required_role="MODERATOR",
            )
        card = await self.data_manager.get_model_by_field("id", card_id)
        if not card:
            raise CardNotFoundError(
                field="id", value=card_id, detail="Карточка не найдена"
            )
        existing_card = await self.data_manager.get_model_by_field("title", data.title)
        if existing_card and existing_card.id != card_id:
            raise CardAlreadyExistsError(
                field="title",
                value=data.title,
                detail="Карточка с таким названием уже существует",
            )
        if image:
            await self._update_card_image(card, image)
        updated_card = await self.data_manager.update_card(card, data)
        serialized_card = await self.data_manager.get_model_by_field(
            "id", updated_card.id
        )
        return CardResponseSchema.model_validate(serialized_card)

    async def _update_card_image(
        self,
        card: Card,
        file: UploadFile,
    ) -> None:
        file_content = await file.read()
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidFileTypeError()
        old_image_url = None
        if hasattr(card, "image") and card.image:
            old_image_url = card.image
            self.logger.info("Текущее изображение: %s", old_image_url)
        else:
            self.logger.info("Изображение не установлено")
        try:
            image_url = await self.s3_data_manager.process_card_image(
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

        await self.data_manager.update_image(card, image_url)

    async def get_all_cards(
        self, pagination: PaginationParams
    ) -> List[CardResponseSchema]:
        cards, total = await self.data_manager.get_all_cards(pagination=pagination)
        return [CardResponseSchema.model_validate(cat) for cat in cards], total

    async def get_card_by_id(self, card_id: int) -> CardResponseSchema:
        card = await self.data_manager.get_model_by_field("id", card_id)
        if not card:
            raise CardNotFoundError(
                field="id", value=card, detail="Карточка не найдена"
            )
        return CardResponseSchema.model_validate(card)

    async def delete_card(self, user: UserModel, card_id: int) -> None:
        if not user.role.MODERATOR:
            raise ForbiddenError(
                detail="Недостаточно прав для обновления категории",
                required_role="MODERATOR",
            )
        card = await self.data_manager.get_model_by_field("id", card_id)
        if not card:
            raise CardNotFoundError(
                field="id", value=card_id, detail="Карточка не найдена"
            )
        await self.data_manager.delete_item(card_id)
