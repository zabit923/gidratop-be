"""
Менеджер данных для регистрации пользователей.
"""

import secrets
from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserExistsError, UserCreationError
from app.core.security.password import PasswordHasher
from app.models import UserModel, UserRole
from app.schemas import UserSchema, RegistrationRequestSchema
from app.services.v1.base import BaseEntityManager


class RegisterDataManager(BaseEntityManager[UserSchema]):
    """
    Менеджер данных для регистрации пользователей.

    Отвечает за:
    - Валидацию уникальности данных
    - Создание моделей пользователей
    - Операции с БД
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def validate_user_uniqueness(self, username: str, email: str, phone: Optional[str] = None) -> None:
        """
        Проверяет уникальность данных пользователя одним запросом.

        Args:
            username: Имя пользователя
            email: Email пользователя
            phone: Телефон пользователя (опционально)

        Raises:
            UserExistsError: Если найден дубликат
        """
        conditions = [
            UserModel.username == username,
            UserModel.email == email
        ]

        if phone:
            conditions.append(UserModel.phone == phone)

        statement = select(UserModel).where(or_(*conditions))
        existing_user = await self.get_one(statement)

        if existing_user:
            # Определяем какое поле дублируется
            if existing_user.username == username:
                raise UserExistsError("username", username)
            elif existing_user.email == email:
                raise UserExistsError("email", email)
            elif phone and existing_user.phone == phone:
                raise UserExistsError("phone", phone)

    async def create_user_from_registration(self, user_data: RegistrationRequestSchema) -> UserModel:
        """
        Создает пользователя из данных регистрации.

        Args:
            user_data: Данные регистрации

        Returns:
            UserModel: Созданный пользователь

        Raises:
            UserCreationError: При ошибке создания
        """
        try:
            user_model = UserModel(
                username=user_data.username,
                email=user_data.email,
                phone=user_data.phone,
                hashed_password=PasswordHasher.hash_password(user_data.password),
                role=UserRole.USER,
                is_active=True,
                is_verified=False,
                referral_code=self._generate_referral_code(),
            )

            created_user = await self.add_one(user_model)

            self.logger.info(
                "Пользователь создан в базе данных: ID=%s", created_user.id
            )
            return created_user

        except Exception as e:
            self.logger.error("Ошибка создания пользователя в БД: %s", e, exc_info=True)
            raise UserCreationError("Не удалось создать пользователя") from e

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
        return await self.get_one(statement)

    def _generate_referral_code(self) -> str:
        """
        Генерирует уникальный реферальный код.

        Returns:
            str: Реферальный код
        """
        random_part = secrets.randbelow(99999999)
        return f"REF{random_part:08d}"
