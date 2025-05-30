from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connections.database import get_db_session
from app.routes.base import BaseRouter
from app.schemas import RegistrationRequestSchema, RegistrationResponseSchema
from app.services.v1.registration.service import RegisterService


class RegisterRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="register", tags=["Registration"])

    def configure(self):
        @self.router.post(
            path="",
            response_model=RegistrationResponseSchema,
        )
        async def registration_user(
            new_user: RegistrationRequestSchema,
            session: AsyncSession = Depends(get_db_session),
        ) -> RegistrationResponseSchema:
            """
            ## 📝 Регистрация нового пользователя

            Регистрирует нового пользователя в системе и отправляет письмо для подтверждения email

            ### Args:
            * **username**: Имя пользователя
            * **email**: Email пользователя
            * **password**: Пароль пользователя
            * **phone**: Телефон пользователя (опционально)

            ### Returns:
            * Информация о созданном пользователе и статус операции
            """
            return await RegisterService(session).create_user(new_user)
