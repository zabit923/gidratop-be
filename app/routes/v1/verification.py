"""
Роутер для верификации email пользователей.

Модуль содержит маршруты для подтверждения email адресов,
повторной отправки писем верификации и проверки статуса.

Routes:
    POST /verification/resend - Повторная отправка письма верификации
    GET /verification/status/{email} - Проверка статуса верификации

Classes:
    VerificationRouter: Класс для настройки маршрутов верификации
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.database import get_db_session
from app.routes.base import BaseRouter
from app.schemas import (
    ResendVerificationRequestSchema,
    ResendVerificationResponseSchema,
    VerificationStatusResponseSchema
)
from app.schemas.v1.users.exception import UserNotFoundResponseSchema
from app.services.v1.registration.service import RegisterService


class VerificationRouter(BaseRouter):
    """
    Класс для настройки маршрутов верификации email.

    Предоставляет маршруты для:
    - Повторной отправки писем верификации
    - Проверки статуса верификации email
    - Подтверждения email по токену

    Attributes:
        router (APIRouter): FastAPI роутер с настроенными маршрутами
    """

    def __init__(self):
        """
        Инициализирует роутер верификации.
        """
        super().__init__(prefix="verification", tags=["Верификация"])

    def configure(self):
        """
        Настраивает все маршруты верификации.

        Определяет endpoints для повторной отправки писем верификации,
        проверки статуса и подтверждения email.
        """

        @self.router.post(
            path="/resend",
            response_model=ResendVerificationResponseSchema,
            summary="Повторная отправка письма верификации",
            description="Отправляет новое письмо для подтверждения email адреса",
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
            result = await RegisterService(session).resend_verification_email(request.email)
            return ResendVerificationResponseSchema(
                email=request.email,
                message=result.get("message", "Письмо верификации отправлено")
            )

        @self.router.get(
            path="/status/{email}",
            response_model=VerificationStatusResponseSchema,
            summary="Проверка статуса верификации",
            description="Проверяет, подтвержден ли email адрес пользователя",
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
            is_verified = await RegisterService(session).check_verification_status(email)
            return VerificationStatusResponseSchema(
                email=email,
                is_verified=is_verified
            )
