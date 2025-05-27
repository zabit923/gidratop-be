from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import UserSchema
from app.services.v1.base import BaseEntityManager


class RegisterDataManager(BaseEntityManager[UserSchema]):
    """
    Менеджер данных для регистрации пользователя в БД.

    Реализует низкоуровневые операции для работы с таблицей пользователей.
    Обрабатывает исключения БД и преобразует их в доменные исключения.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[UserSchema]): Схема сериализации данных
        model (Type[UserModel]): Модель пользователя

    Methods:
        add_user: Добавление пользователя в БД
        get_user_by_field: Получение пользователя по полю
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def add_user(self, user: UserModel) -> UserModel:
        """
        Добавляет нового пользователя в базу данных.

        Args:
            user: Пользователь для добавления.

        Returns:
            UserCredentialsSchema: Данные пользователя.

        #TODO: Пересмотреть (слишком просто :))
        """

        return await self.add_one(user)
