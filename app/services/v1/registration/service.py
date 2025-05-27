"""
Сервис для регистрации пользователей.

Модуль содержит бизнес-логику для регистрации новых пользователей,
включая валидацию данных, проверку уникальности и создание аккаунтов.
Поддерживает как обычную регистрацию, так и OAuth провайдеров.

Classes:
    RegisterService: Основной сервис для регистрации пользователей
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.users import UserCreationError, UserExistsError
from app.core.security.password import PasswordHasher
from app.models import UserModel, UserRole
from app.schemas import (RegistrationDataSchema, RegistrationRequestSchema,
                         RegistrationResponseSchema)
from app.services.v1.base import BaseService

from .data_manager import RegisterDataManager


class RegisterService(BaseService):
    """
    Сервис для регистрации пользователей.

    Предоставляет методы для создания новых пользователей с полной валидацией
    данных, проверкой уникальности и безопасным хешированием паролей.
    Поддерживает как стандартную регистрацию, так и OAuth провайдеров (в перспективе).

    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с базой данных
        data_manager (RegisterDataManager): Менеджер данных для операций с пользователями

    Methods:
        create_user: Создание нового пользователя через веб-форму
        _create_user_internal: Внутренний метод создания пользователя
        _validate_user_uniqueness: Проверка уникальности данных пользователя

    Example:
        ```python
        async with get_db_session() as session:
            service = RegisterService(session)
            user_data = RegistrationRequestSchema(
                username="john_doe",
                email="john@example.com",
                phone="+7 (999) 123-45-67",
                password="SecurePass123!"
            )
            result = await service.create_user(user_data)
        ```
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис регистрации.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных
        """
        super().__init__(session)
        self.data_manager = RegisterDataManager(session)

    async def create_user(
        self, new_user: RegistrationRequestSchema
    ) -> RegistrationResponseSchema:
        """
        Создает нового пользователя через веб-форму регистрации.

        Выполняет полный цикл регистрации пользователя: валидацию данных,
        проверку уникальности, создание записи в базе данных и формирование ответа.

        Args:
            new_user (RegistrationRequestSchema): Данные пользователя из формы регистрации

        Returns:
            RegistrationResponseSchema: Схема ответа с данными созданного пользователя

        Raises:
            UserExistsError: Если пользователь с такими данными уже существует
            UserCreationError: При ошибке создания пользователя в базе данных

        Example:
            ```python
            registration_data = RegistrationRequestSchema(
                username="john_doe",
                email="john@example.com",
                phone="+7 (999) 123-45-67",
                password="SecurePass123!"
            )
            response = await service.create_user(registration_data)
            # response.data.user_id = 123
            # response.data.email = "john@example.com"
            ```
        """

        self.logger.info("Начало регистрации пользователя: %s", new_user.username)

        # Создаем пользователя через внутренний метод
        created_user = await self._create_user_internal(new_user)

        # Формируем данные ответа
        registration_data = RegistrationDataSchema(
            user_id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            role=created_user.role.value,
            is_active=created_user.is_active,
            is_verified=created_user.is_verified,
            created_at=created_user.created_at,
            referral_code=created_user.referral_code,
        )

        self.logger.info("Пользователь успешно зарегистрирован: ID=%s", created_user.id)

        return RegistrationResponseSchema(
            message="Регистрация успешно завершена", item=registration_data
        )

    async def _validate_user_uniqueness(self, user: RegistrationRequestSchema) -> None:
        """
        Проверяет уникальность данных пользователя.

        Проверяет, что пользователь с указанными username, email или телефоном
        еще не зарегистрирован в системе.

        Args:
            user (RegistrationSchema): Данные пользователя для проверки

        Raises:
            UserExistsError: Если найден пользователь с такими же данными

        Note:
            Проверка телефона выполняется только если он указан в данных.
        """
        # Проверка username
        existing_user = await self.data_manager.get_item_by_field(
            "username", user.username
        )
        if existing_user:
            self.logger.warning(
                "Попытка регистрации с существующим username: %s", user.username
            )
            raise UserExistsError("username", user.username)

        # Проверка email
        existing_user = await self.data_manager.get_item_by_field("email", user.email)
        if existing_user:
            self.logger.warning(
                "Попытка регистрации с существующим email: %s", user.email
            )
            raise UserExistsError("email", user.email)

        # Проверка телефона (если указан)
        if user.phone:
            existing_user = await self.data_manager.get_item_by_field(
                "phone", user.phone
            )
            if existing_user:
                self.logger.warning(
                    "Попытка регистрации с существующим телефоном: %s", user.phone
                )
                raise UserExistsError("phone", user.phone)

    async def _create_user_internal(self, user: RegistrationRequestSchema) -> UserModel:
        """
        Внутренний метод создания пользователя в базе данных.

        Выполняет низкоуровневые операции по созданию пользователя:
        проверку уникальности, хеширование пароля и сохранение в БД.

        Args:
            user (RegistrationSchema): Данные нового пользователя

        Returns:
            UserModel: Созданная модель пользователя из базы данных

        Raises:
            UserExistsError: Если пользователь с таким email, username или телефоном уже существует
            UserCreationError: При ошибке создания пользователя в базе данных

        Note:
            - Поддерживает данные как из веб-формы, так и от OAuth провайдеров
            - Проверяет уникальность email, username и телефона
            - Автоматически хеширует пароль перед сохранением
            - Генерирует реферальный код для нового пользователя
        """
        self.logger.debug(
            "Создание пользователя с данными: username=%s, email=%s",
            user.username,
            user.email,
        )

        # Проверяем уникальность данных пользователя
        await self._validate_user_uniqueness(user)

        # Создаем модель пользователя
        user_model = UserModel(
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=PasswordHasher.hash_password(user.password),
            role=UserRole.USER,
            is_active=True,
            is_verified=False,
            # Генерируем реферальный код (можно добавить логику генерации)
            referral_code="0",  # TODO: реализовать позже #self._generate_referral_code(user.username)
        )

        try:
            # Сохраняем пользователя в базе данных
            created_user = await self.data_manager.add_one(user_model)

            self.logger.info(
                "Пользователь создан в базе данных: ID=%s", created_user.id
            )
            return created_user

        except Exception as e:
            self.logger.error(
                "Ошибка при создании пользователя в БД: %s", e, exc_info=True
            )
            raise UserCreationError(
                "Не удалось создать пользователя. Пожалуйста, попробуйте позже."
            ) from e
