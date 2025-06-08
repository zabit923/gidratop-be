"""
FUNCTIONAL ТЕСТЫ для роутера аутентификации.

"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.v1.users import UserModel
from app.core.security.password import PasswordHasher
from tests.utils import create_test_user_data


class TestAuthAPI:
    """Functional тесты API аутентификации"""

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_successful_authentication(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест успешной аутентификации пользователя.

        Что тестируем:
        1. HTTP запрос POST /api/v1/auth с валидными данными
        2. Получение корректного HTTP ответа (200, структура JSON)
        3. Реальная проверка пароля из БД
        4. Генерация JWT токенов

        Фикстуры:
        - client: HTTP клиент с реальной БД
        - db_session: прямой доступ к БД для создания тестового пользователя

        Почему functional:
        - Нет моков AuthService - полный цикл до БД
        - Проверяем реальную аутентификацию
        """
        # 1. Создаем пользователя в БД
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        # 2. HTTP запрос аутентификации
        auth_data = {
            "username": user_data["email"],  # Можно использовать email как username
            "password": user_data["password"]
        }
        
        response = await client.post("/api/v1/auth", data=auth_data)

        # 3. Проверка HTTP ответа
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        
        # token_data = data["data"]
        token_data = data
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "token_type" in token_data
        assert "expires_in" in token_data
        assert token_data["token_type"] == "Bearer"
        assert isinstance(token_data["expires_in"], int)

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_authentication_with_username(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест аутентификации по имени пользователя.
        """
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        auth_data = {
            "username": user_data["username"],  # Используем username
            "password": user_data["password"]
        }
        
        response = await client.post("/api/v1/auth", data=auth_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_authentication_with_phone(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест аутентификации по номеру телефона.
        """
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            phone=user_data.get("phone"),
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        auth_data = {
            "username": user_data["phone"],  # Используем телефон
            "password": user_data["password"]
        }
        
        response = await client.post("/api/v1/auth", data=auth_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_authentication_with_cookies(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест аутентификации с использованием cookies.

        Что тестируем:
        1. Параметр use_cookies=true в URL
        2. Установку HTTP cookies в ответе
        3. Отсутствие токенов в JSON (они в cookies)
        """
        # Создаем пользователя
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        # Аутентификация с cookies
        auth_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        response = await client.post("/api/v1/auth?use_cookies=true", data=auth_data)
        assert response.status_code == 200

        # Проверяем cookies
        set_cookie_headers = response.headers.get_list("set-cookie")
        assert any("access_token=" in cookie for cookie in set_cookie_headers)
        assert any("refresh_token=" in cookie for cookie in set_cookie_headers)

        # Проверяем что токены в JSON равны None
        data = response.json()
        token_data = data
        assert token_data["access_token"] is None
        assert token_data["refresh_token"] is None

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_invalid_credentials(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест аутентификации с неверными учетными данными.

        Бизнес-правило: неверные данные должны возвращать 401
        """
        # Создаем пользователя
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        # Неверный пароль
        auth_data = {
            "username": user_data["email"],
            "password": "wrong_password"
        }
        
        response = await client.post("/api/v1/auth", data=auth_data)
        assert response.status_code == 401
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_inactive_user_authentication(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест аутентификации неактивного пользователя.

        Бизнес-правило: неактивные пользователи не могут войти в систему
        """
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=False,  # Пользователь неактивен
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        auth_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        response = await client.post("/api/v1/auth", data=auth_data)
        assert response.status_code == 403
        
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_nonexistent_user_authentication(self, client: AsyncClient):
        """
        Тест аутентификации несуществующего пользователя.
        """
        auth_data = {
            "username": "nonexistent@example.com",
            "password": "any_password"
        }
        
        response = await client.post("/api/v1/auth", data=auth_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_refresh_token_success(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест успешного обновления токена.

        Что тестируем:
        1. Получение токенов через аутентификацию
        2. Использование refresh токена для получения нового access токена
        3. Ротация refresh токенов
        """
        # Создаем пользователя и аутентифицируемся
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        # Получаем токены
        auth_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        auth_response = await client.post("/api/v1/auth", data=auth_data)
        assert auth_response.status_code == 200
        
        auth_data = auth_response.json()["data"]
        refresh_token = auth_data["refresh_token"]

        # Обновляем токен
        response = await client.post(
            "/api/v1/auth/refresh",
            headers={"refresh-token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        token_data = data["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        
        # Новые токены должны отличаться от старых
        assert token_data["access_token"] != auth_data["access_token"]
        assert token_data["refresh_token"] != refresh_token

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_refresh_token_with_cookies(self, client: AsyncClient, db_session: AsyncSession):
        """
        Тест обновления токена через cookies.
        """
        # Создаем пользователя и аутентифицируемся с cookies
        user_data = create_test_user_data()
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=PasswordHasher.hash_password(user_data["password"]),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        auth_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        auth_response = await client.post("/api/v1/auth?use_cookies=true", data=auth_data)
        assert auth_response.status_code == 200

        # Извлекаем refresh токен из cookies
        cookies = auth_response.cookies
        refresh_token = cookies.get("refresh_token")
        assert refresh_token is not None

        # Обновляем токен через cookies
        response = await client.post(
            "/api/v1/auth/refresh?use_cookies=true",
            cookies={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_refresh_token_missing(self, client: AsyncClient):
        """
        Тест обновления токена без предоставления refresh токена.
        """
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.functional
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """
        Тест обновления токена с невалидным refresh токеном.
        """
        response = await client.post(
            "/api/v1/auth/refresh",
            headers={"refresh-token": "invalid_token"}
        )
        assert response.status_code == 422