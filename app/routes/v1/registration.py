"""
Роутер для регистрации пользователей.

Модуль содержит маршруты для регистрации новых пользователей
и подтверждения их email адресов.

Routes:
    POST /register - Регистрация нового пользователя
    GET /register/verify-email/{token} - Подтверждение email по токену

Classes:
    RegisterRouter: Класс для настройки маршрутов регистрации
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.database import get_db_session
from app.routes.base import BaseRouter
from app.schemas import (
    VerificationResponseSchema,
    RegistrationRequestSchema,
    RegistrationResponseSchema,
    UserNotFoundResponseSchema,
    UserCreationResponseSchema,
    UserExistsResponseSchema,
    TokenExpiredResponseSchema,
    TokenInvalidResponseSchema
)

from app.services.v1.registration.service import RegisterService


class RegisterRouter(BaseRouter):
    """
    Класс для настройки маршрутов регистрации.

    Предоставляет маршруты для:
    - Регистрации новых пользователей
    - Подтверждения email адресов по токену

    Attributes:
        router (APIRouter): FastAPI роутер с настроенными маршрутами
    """
    def __init__(self):
        """
        Инициализирует роутер регистрации.
        """
        super().__init__(prefix="register", tags=["Регистрация"])

    def configure(self):
        """
        Настраивает все маршруты регистрации.

        Определяет endpoints для регистрации пользователей
        и подтверждения их email адресов.
        """
        @self.router.post(
            path="",
            response_model=RegistrationResponseSchema,
            summary="Регистрация нового пользователя",
            description="Регистрирует нового пользователя и отправляет письмо верификации",
            responses={
                201: {
                    "model": RegistrationResponseSchema,
                    "description": "Пользователь успешно зарегистрирован",
                },
                409: {
                    "model": UserExistsResponseSchema,
                    "description": "Пользователь с таким email/username/телефоном уже существует",
                },
                500: {
                    "model": UserCreationResponseSchema,
                    "description": "Ошибка при создании пользователя",
                },
            },
        )
        async def registration_user(
            new_user: RegistrationRequestSchema,
            session: AsyncSession = Depends(get_db_session),
        ) -> RegistrationResponseSchema:
            """
            ## 📝 Регистрация нового пользователя

            Регистрирует нового пользователя в системе и отправляет письмо для подтверждения email.
            После успешной регистрации пользователь получит письмо с ссылкой для активации аккаунта.

            ### Параметры:
            * **username**: Уникальное имя пользователя (3-50 символов)
            * **email**: Email адрес пользователя (должен быть уникальным)
            * **password**: Пароль (минимум 8 символов, должен содержать буквы и цифры)
            * **phone**: Номер телефона в формате +7 (XXX) XXX-XX-XX (опционально)

            ### Returns:
            * **user_id**: Уникальный идентификатор созданного пользователя
            * **username**: Имя пользователя
            * **email**: Email адрес
            * **is_verified**: Статус подтверждения email (false для новых пользователей)
            * **referral_code**: Реферальный код пользователя

            ### Процесс регистрации:
            1. Валидация входных данных
            2. Проверка уникальности email, username и телефона
            3. Создание пользователя в базе данных
            4. Генерация токена верификации
            5. Отправка письма с ссылкой подтверждения

            ### Примечания:
            * Пользователь создается с is_verified=false
            * Для полного доступа необходимо подтвердить email
            * Письмо верификации действительно 24 часа
            """
            return await RegisterService(session).create_user(new_user)

        @self.router.get(
            path="/verify-email/{token}",
            response_model=VerificationResponseSchema,
            summary="Подтверждение email адреса",
            description="Подтверждает email адрес пользователя по токену из письма",
            responses={
                200: {
                    "model": VerificationResponseSchema,
                    "description": "Email успешно подтвержден",
                },
                400: {
                    "model": TokenInvalidResponseSchema,
                    "description": "Недействительный токен верификации",
                },
                419: {
                    "model": TokenExpiredResponseSchema,
                    "description": "Срок действия токена истек",
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        async def verify_email(
            token: str,
            session: AsyncSession = Depends(get_db_session),
        ) -> VerificationResponseSchema:
            """
            ## ✉️ Подтверждение email адреса

            Подтверждает email адрес пользователя по токену из письма верификации.
            После подтверждения пользователь получает полный доступ к системе.

            ### Параметры:
            * **token**: Токен верификации из письма

            ### Returns:
            * **user_id**: ID пользователя
            * **success**: Статус операции
            * **message**: Сообщение о результате
            * **verified_at**: Время подтверждения email

            ### Процесс верификации:
            1. Декодирование и валидация токена
            2. Проверка срока действия токена
            3. Поиск пользователя в базе данных
            4. Обновление статуса is_verified=true
            5. Отправка письма об успешной регистрации

            ### Примечания:
            * Токен одноразовый и имеет ограниченный срок действия
            * После подтверждения пользователь может войти в систему
            * Если email уже подтвержден, возвращается соответствующее сообщение
            * При истечении токена необходимо запросить повторную отправку
            """
            return await RegisterService(session).verify_email(token)