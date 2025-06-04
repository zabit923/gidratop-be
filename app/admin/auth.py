from fastapi.params import Depends
from redis import Redis
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AuthProvider
from starlette_admin.exceptions import LoginFailed

from app.core.connections.cache import get_redis_client
from app.core.connections.database import get_db_session
from app.core.security.password import PasswordHasher
from app.services.v1.auth.service import AuthService


class CustomAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
        redis: Redis = Depends(get_redis_client),
    ) -> Response:
        async for session in get_db_session():
            service = AuthService(session, redis)
            user = await service.data_manager.get_user_by_identifier(username)
            if not user or not PasswordHasher.verify(user.hashed_password, password):
                raise LoginFailed("Invalid username or password")
            request.session.update({"username": username})
        return response

    async def is_authenticated(
        self, request: Request, redis: Redis = Depends(get_redis_client)
    ) -> bool:
        async for session in get_db_session():
            username = request.session.get("username")
            if username:
                service = AuthService(session, redis)
                user = await service.data_manager.get_user_by_identifier(username)
                if user:
                    request.state.user = user
                    return True
        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        custom_app_title = "Gidratop Admin"
        return AdminConfig(
            app_title=custom_app_title,
        )

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
