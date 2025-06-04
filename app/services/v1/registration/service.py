"""
Сервис регистрации пользователей.

Обеспечивает полный цикл регистрации: валидацию, создание пользователя,
отправку письма верификации и подтверждение email.

Classes:
    RegisterService: Основной сервис для регистрации пользователей
"""


from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.core.integrations.mail import AuthEmailDataManager

from app.core.security.token import TokenManager
from app.models import UserModel
from app.schemas import (RegistrationDataSchema, RegistrationRequestSchema,
                         RegistrationResponseSchema,
                         VerificationResponseSchema,
                         ResendVerificationResponseSchema)
from app.services.v1.base import BaseService

from .data_manager import RegisterDataManager


class RegisterService(BaseService):
    """
    Сервис для регистрации и верификации пользователей.

    Основные операции:
    1. Регистрация нового пользователя
    2. Отправка письма верификации
    3. Подтверждение email по токену
    4. Повторная отправка письма верификации

    Attributes:
        session: Асинхронная сессия базы данных
        data_manager: Менеджер данных для операций с пользователями
        email_data_manager: Менеджер для отправки email
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует сервис регистрации.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных
        """
        super().__init__(session)
        self.data_manager = RegisterDataManager(session)
        self.email_data_manager = AuthEmailDataManager()

    async def create_user(
        self, user_data: RegistrationRequestSchema
    ) -> RegistrationResponseSchema:
        """
        Создает нового пользователя и отправляет письмо верификации.

        Полный процесс:
        1. Валидация уникальности данных
        2. Создание пользователя в БД
        3. Генерация токена верификации
        4. Отправка письма верификации

        Args:
            user_data: Данные для регистрации пользователя

        Returns:
            RegistrationResponseSchema: Данные созданного пользователя

        Raises:
            UserExistsError: Если пользователь с такими данными уже существует
            UserCreationError: При ошибке создания в БД
        """

        self.logger.info("Начало регистрации пользователя: %s", user_data.username)

        # Валидируем уникальность данных
        await self.data_manager.validate_user_uniqueness(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone
        )

        # Создаем пользователя через внутренний метод
        created_user = await self.data_manager.create_user_from_registration(user_data)

        # Отправляем письмо верификации
        await self._send_verification_email(created_user)

        # Формируем данные ответа
        response_data = self._build_registration_response(created_user)

        self.logger.info("Пользователь успешно зарегистрирован: ID=%s", created_user.id)

        return RegistrationResponseSchema(
            message="Регистрация успешно завершена",
            item=response_data
        )

    async def verify_email(self, token: str) -> VerificationResponseSchema:
        """
        Подтверждает email пользователя по токену.

        Args:
            token: Токен верификации

        Returns:
            VerificationResponseSchema: Результат верификации
        """
        self.logger.info("Попытка верификации email по токену")


        # Декодируем и валидируем токен
        payload = TokenManager.verify_token(token)
        user_id = TokenManager.validate_verification_token(payload)

        # Получаем пользователя
        user = await self.data_manager.get_item_by_field("id", user_id)
        if not user:
            self.logger.warning("Пользователь не найден", extra={"user_id": user_id})
            raise UserNotFoundError(field="id", value=user_id)

        # Проверяем, не верифицирован ли уже
        if user.is_verified:
            return VerificationResponseSchema(
                user_id=user_id,
                success=True,
                message="Email уже был подтвержден ранее.",
            )

        # Подтверждаем email
        await self.data_manager.update_items(user_id, {"is_verified": True})

        # Отправляем письмо об успешной регистрации
        await self._send_registration_success_email(user)

        self.logger.info("Email успешно подтвержден", extra={"user_id": user_id})

        return VerificationResponseSchema(
            user_id=user_id,
            message="Email успешно подтвержден. Теперь вы можете войти в систему.",
        )

    async def resend_verification_email(self, email: str) -> dict:
        """
        Повторно отправляет письмо верификации.

        Args:
            email: Email пользователя

        Returns:
            dict: Статус операции

        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        # Поиск пользователя по email
        user_model = await self.data_manager.get_user_by_identifier(email)
        if not user_model:
            raise UserNotFoundError(field="email", value=email)

        # Проверка статуса
        if user_model.is_verified:
            return ResendVerificationResponseSchema(
                message="Email уже подтвержден"
            )

        # Отправка письма
        await self._send_verification_email(user_model)

        return ResendVerificationResponseSchema(
            message="Письмо с токеном верификации отправлено повторно"
        )

    async def check_verification_status(self, email: str) -> bool:
        """
        Проверяет статус верификации email пользователя

        Args:
            email: Email пользователя

        Returns:
            bool: True если email подтвержден, иначе False

        Raises:
            UserNotFoundError: Если пользователь с указанным email не найден
        """
        user = await self.data_manager.get_item_by_field("email", email)
        if not user:
            self.logger.error("Пользователь с email '%s' не найден", email)
            raise UserNotFoundError(field="email", value=email)

        return user.is_verified

    def _validate_verification_token(self, token: str) -> int:
        """
        Валидирует токен верификации и возвращает user_id.

        Args:
            token: Токен для проверки

        Returns:
            int: ID пользователя

        Raises:
            TokenInvalidError: Если токен недействителен
            TokenExpiredError: Если токен истек
        """
        try:
            payload = TokenManager.verify_token(token)
            return TokenManager.validate_verification_token(payload)
        except Exception as e:
            self.logger.error("Ошибка валидации токена верификации: %s", e)
            raise

    async def _send_verification_email(self, user: UserModel) -> None:
        """
        Отправляет письмо с токеном верификации пользователю.

        Args:
            user: Модель пользователя, которому отправляется письмо
        """
        try:
            verification_token = TokenManager.generate_verification_token(user.id)
            await self.email_data_manager.send_verification_email(
                to_email=user.email,
                user_name=user.username,
                verification_token=verification_token,
            )
            self.logger.info(
                "Письмо верификации отправлено",
                extra={"user_id": user.id, "email": user.email}
            )
        except Exception as e:
            # Не прерываем регистрацию, если письмо не отправилось
            self.logger.error(
            "Ошибка при отправке письма верификации: %s",
            e,
            extra={"user_id": user.id, "email": user.email}
        )

    async def _send_registration_success_email(self, user_schema) -> None:
        """
        Отправляет письмо об успешной регистрации.

        Args:
            user_schema: Схема пользователя
        """
        try:
            await self.email_data_manager.send_registration_success_email(
                to_email=user_schema.email,
                user_name=user_schema.username
            )
            self.logger.info(
                "Письмо об успешной регистрации отправлено",
                extra={"user_id": user_schema.id, "email": user_schema.email}
            )
        except Exception as e:
            self.logger.error(
                "Ошибка отправки письма об успешной регистрации: %s",
                e,
                extra={"user_id": user_schema.id, "email": user_schema.email}
            )

    def _build_registration_response(self, user_model: UserModel) -> RegistrationDataSchema:
        """
        Формирует данные ответа регистрации.

        Args:
            user_model: Модель пользователя

        Returns:
            RegistrationDataSchema: Данные ответа регистрации
        """
        return RegistrationDataSchema(
            user_id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            role=user_model.role.value,
            is_active=user_model.is_active,
            is_verified=user_model.is_verified,
            created_at=user_model.created_at,
            referral_code=user_model.referral_code,
        )
