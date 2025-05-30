"""
Базовый менеджер данных для работы с пользователями.
"""

from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import UserSchema
from app.services.v1.base import BaseEntityManager


class UserDataManager(BaseEntityManager[UserSchema]):
    """
    Базовый менеджер для работы с пользователями.

    Содержит общие методы для работы с пользователями,
    которые используются в разных сервисах.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def get_user_by_identifier(self, identifier: str) -> Optional[UserModel]:
        """
        Находит пользователя по email, username или телефону.

        Args:
            identifier: Email, username или телефон

        Returns:
            UserModel | None: Найденная модель или None
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
