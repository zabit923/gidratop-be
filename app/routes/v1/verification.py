"""
Роутер для верификации email пользователей.

Модуль содержит маршруты для подтверждения email адресов,
повторной отправки писем верификации и проверки статуса.

Routes:
    GET /register/verify-email/{token} - Подтверждение email по токену
    POST /verification/resend - Повторная отправка письма верификации
    GET /verification/status/{email} - Проверка статуса верификации

Classes:
    VerificationRouter: Класс для настройки маршрутов верификации
"""
from typing import Optional
from fastapi import Depends
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.connections.cache import get_redis_client
from app.core.connections.database import get_db_session
from app.routes.base import BaseRouter
from app.schemas import (
    VerificationResponseSchema,
    ResendVerificationRequestSchema,
    ResendVerificationResponseSchema,
    VerificationStatusResponseSchema,
    UserNotFoundResponseSchema,
    TokenExpiredResponseSchema,
    TokenInvalidResponseSchema
)

from app.services.v1.registration.service import RegisterService


class VerificationRouter(BaseRouter):
    """
    Класс для настройки маршрутов верификации email.

    Предоставляет маршруты для:
    - Подтверждения email адресов по токену
    - Повторной отправки писем верификации
    - Проверки статуса верификации email

    Attributes:
        router (APIRouter): FastAPI роутер с настроенными маршрутами
    """

    def __init__(self):
        """
        Инициализирует роутер верификации.
        """
        super().__init__(prefix="verification", tags=["Verification"])

    def configure(self):
        """
        Настраивает все маршруты верификации.

        Определяет endpoints для повторной отправки писем верификации,
        проверки статуса и подтверждения email.
        """

        @self.router.get(
            path="/verify-email/{token}",
            response_model=VerificationResponseSchema,
            summary="Подтверждение email адреса",
            # description="Подтверждает email адрес пользователя по токену из письма",
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
            redis: Optional[Redis] = Depends(get_redis_client),
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
            * После подтверждения пользователь может войти в систему (точнее производить покупки и прочие действия на сайте)
            * Если email уже подтвержден, возвращается соответствующее сообщение
            * При истечении токена необходимо запросить повторную отправку
            """
            return await RegisterService(session, redis).verify_email(token)

        @self.router.post(
            path="/resend",
            response_model=ResendVerificationResponseSchema,
            summary="Повторная отправка письма верификации",
            # description="Отправляет новое письмо для подтверждения email адреса",
            responses={
                200: {
                    "model": ResendVerificationResponseSchema,
                    "description": "Письмо верификации отправлено",
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        async def resend_verification_email(
            request: ResendVerificationRequestSchema,
            session: AsyncSession = Depends(get_db_session),
            redis: Optional[Redis] = Depends(get_redis_client),
        ) -> ResendVerificationResponseSchema:
            """
            ## 📧 Повторная отправка письма для подтверждения email

            Отправляет новое письмо для подтверждения email адреса зарегистрированного пользователя.
            Используется когда пользователь не получил первоначальное письмо или оно истекло.

            ### Параметры:
            * **email**: Email адрес пользователя для повторной отправки

            ### Returns:
            * **message**: Сообщение о статусе отправки
            * **email**: Email, на который отправлено письмо

            ### Примечания:
            * Если email уже подтвержден, возвращается соответствующее сообщение
            * Ограничение на частоту отправки писем (защита от спама)
            * Новый токен верификации генерируется для каждой отправки
            """
            result = await RegisterService(session, redis).resend_verification_email(request.email)
            return ResendVerificationResponseSchema(
                email=request.email,
                message=result.get("message", "Письмо верификации отправлено")
            )

        @self.router.get(
            path="/status/{email}",
            response_model=VerificationStatusResponseSchema,
            summary="Проверка статуса верификации",
            # description="Проверяет, подтвержден ли email адрес пользователя",
            responses={
                200: {
                    "model": VerificationStatusResponseSchema,
                    "description": "Статус верификации получен",
                },
                404: {
                    "model": UserNotFoundResponseSchema,
                    "description": "Пользователь не найден",
                },
            },
        )
        async def check_verification_status(
            email: str,
            session: AsyncSession = Depends(get_db_session),
            redis: Optional[Redis] = Depends(get_redis_client),
        ) -> VerificationStatusResponseSchema:
            """
            ## ✅ Проверка статуса верификации

            Проверяет, подтвержден ли email адрес пользователя в системе.
            Полезно для проверки необходимости повторной отправки письма.

            ### Параметры:
            * **email**: Email адрес для проверки статуса

            ### Returns:
            * **email**: Проверяемый email адрес
            * **is_verified**: Статус верификации (true/false)
            * **registration_date**: Дата регистрации пользователя
            * **verification_date**: Дата подтверждения email (если подтвержден)

            ### Использование:
            * Проверка перед повторной отправкой письма
            * Отображение статуса в интерфейсе пользователя
            * Валидация для операций, требующих подтвержденный email
            """
            is_verified = await RegisterService(session, redis).check_verification_status(email)
            return VerificationStatusResponseSchema(
                email=email,
                is_verified=is_verified
            )
