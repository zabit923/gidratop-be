"""
Менеджер данных для аутентификации.

Обеспечивает доступ к данным пользователей для операций аутентификации.
"""

import re
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import UserCredentialsSchema
from app.services.v1.base import BaseEntityManager


class AuthDataManager(BaseEntityManager[UserCredentialsSchema]):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserCredentialsSchema, model=UserModel)

    async def get_user_by_identifier(self, identifier: str) -> Optional[UserModel]:
        """
        Получение пользователя по имени пользователя, email или телефону.

        Валидация identifier уже выполнена в Pydantic схеме.

        Args:
            identifier: Имя пользователя, email или телефон (уже валидированный)

        Returns:
            UserModel | None: Пользователь или None, если не найден
        """
        statement = select(UserModel).where(
            or_(
                UserModel.email == identifier,
                UserModel.username == identifier,
                UserModel.phone == identifier
            )
        )

        user = await self.get_one(statement)

        if user:
            self.logger.info(
                "Пользователь найден",
                extra={"identifier": identifier, "user_id": user.id}
            )
        else:
            self.logger.info(
                "Пользователь не найден",
                extra={"identifier": identifier}
            )

        return user
