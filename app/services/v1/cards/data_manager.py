from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.models import Card
from app.schemas import (
    CardCreateSchema,
    CardDataSchema,
    CardUpdateSchema,
    PaginationParams,
)
from app.services.v1.base import BaseEntityManager


class CardDataManager(BaseEntityManager[CardDataSchema]):
    """
    Менеджер данных для работы с карточками.
    Реализует низкоуровневые операции для работы с таблицами карточек в БД.
    Обрабатывает исключения БД и преобразует их в доменные исключения.
    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[CardDataSchema]): Схема сериализации данных
        model (Type[CardModel]): Модель карточки

    Methods:
        add_card: Добавление новой карточки в БД
        update_card: Обновление существующей карточки в БД
        delete_card: Удаление карточки из БД
        get_card_by_id: Получение
        get_all_cards: Получение всех карточек с возможностью пагинации
    """

    def __init__(self, session):
        super().__init__(session=session, schema=CardDataSchema, model=Card)

    async def add_card(self, data: CardCreateSchema) -> Card:
        card_model = self.model(**data.model_dump())
        return await self.add_one(card_model)

    async def update_card(self, card: Card, data: CardUpdateSchema) -> Card:
        card_data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in card_data_dict.items():
            setattr(card, key, value)
        return await self.update_one(card)

    async def update_image(self, card: Card, image_url: str) -> None:
        try:
            await self.update_items(card.id, {"image": image_url})
        except (ValueError, SQLAlchemyError):
            self.logger.error(
                "Не удалось обновить изображение для карточки %s", card.id
            )
            raise RuntimeError(
                f"Не удалось обновить изображение для карточки {card.id}"
            )

    async def get_all_cards(self, pagination=PaginationParams):
        statement = select(Card)
        return await self.get_paginated_items(statement, pagination)
