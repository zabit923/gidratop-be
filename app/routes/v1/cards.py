from typing import Optional

from fastapi import Depends, File, Form, UploadFile
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session
from app.core.integrations.storage import CardS3DataManager, get_card_s3_manager
from app.core.security.auth import get_current_user
from app.models import UserModel
from app.routes.base import BaseRouter
from app.schemas import (
    CardCreateSchema,
    CardListResponseSchema,
    CardResponseSchema,
    CardUpdateSchema,
    Page,
    PaginationParams,
)
from app.services.v1.cards.service import CardService


class CardRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="cards", tags=["Cards"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=CardResponseSchema,
            status_code=status.HTTP_201_CREATED,
            summary="Создание новой карточки",
        )
        async def create_card(
            new_card: CardCreateSchema,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> CardResponseSchema:
            return await CardService(session).create_card(user, new_card)

        @self.router.get(
            path="",
            response_model=CardListResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Получение всех карточек",
        )
        async def get_all_cards(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            session: AsyncSession = Depends(get_db_session),
        ) -> CardListResponseSchema:
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            cards, total = await CardService(session).get_all_cards(
                pagination=pagination
            )
            page = Page(
                items=cards,
                total=total,
                page=pagination.page,
                size=pagination.limit,
            )
            return CardListResponseSchema(data=page)

        @self.router.patch(
            path="/{card_id}",
            response_model=CardResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Обновление карточки",
        )
        async def update_card(
            card_id: int,
            title: Optional[str] = Form(None),
            image: Optional[UploadFile] = File(None),
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
            s3_data_manager: CardS3DataManager = Depends(get_card_s3_manager),
        ) -> CardResponseSchema:
            category_data = CardUpdateSchema(title=title)
            return await CardService(session, s3_data_manager).update_card(
                user, card_id, category_data, image
            )

        @self.router.get(
            path="/{card_id}",
            response_model=CardResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="Получение карточки по ID",
        )
        async def get_card_by_id(
            card_id: int,
            session: AsyncSession = Depends(get_db_session),
        ) -> CardResponseSchema:
            return await CardService(session).get_card_by_id(card_id)

        @self.router.delete(
            path="/{card_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удаление карточки по ID",
        )
        async def delete_card(
            card_id: int,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> None:
            await CardService(session).delete_card(user, card_id)
