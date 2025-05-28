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

        Args:
            identifier: Имя пользователя, email или телефон.

        Returns:
            UserModel | None: Пользователь или None, если пользователь не найден
        """
        try:
            self.logger.info(
                    "Поиск пользователя по идентификатору",
                    extra={"identifier": identifier}
                )

            # Проверяем, является ли identifier email-ом
            if "@" in identifier:
                user = await self.get_model_by_field("email", identifier)
                if user:
                    self.logger.info(
                            "Пользователь найден по email",
                            extra={"identifier": identifier, "user_id": user.id}
                        )
                    return user

            # Проверяем, является ли identifier телефоном
            # Паттерн для телефона в формате +7 (XXX) XXX-XX-XX
            phone_pattern = r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$"
            if re.match(phone_pattern, identifier):
                user = await self.get_model_by_field("phone", identifier)
                if user:
                    self.logger.info(
                            "Пользователь найден по телефону",
                            extra={"identifier": identifier, "user_id": user.id}
                        )
                    return user

            # В противном случае, ищем по имени пользователя
            user = await self.get_model_by_field("username", identifier)
            if user:
                self.logger.info(
                        "Пользователь найден по username",
                        extra={"identifier": identifier, "user_id": user.id}
                    )
                return user

            # Если ничего не найдено, возвращаем None
            return None
        except Exception as e:
            self.logger.error(
                "Ошибка при поиске пользователя",
                extra={"identifier": identifier, "error": str(e)}
            )
            return None
