import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import TestDatabase


class TestRegistrationAPI(TestDatabase):
    """Интеграционные тесты API регистрации"""
    
    @pytest.mark.asyncio
    async def test_successful_registration(self, client: AsyncClient, db_session: AsyncSession):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123",
            "phone": "+7 (999) 123-45-67"
        }
        
        response = await client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        
        # Проверяем, что пользователь создался в БД
        from app.models.v1.user import User
        from sqlalchemy import select
        
        result = await db_session.execute(
            select(User).where(User.email == user_data["email"])
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]

    @pytest.mark.asyncio
    async def test_registration_with_cookies(self, client: AsyncClient, db_session: AsyncSession):
        """Тест регистрации с использованием cookies"""
        user_data = {
            "username": "cookieuser",
            "email": "cookie@example.com",
            "password": "SecurePass123"
        }
        
        response = await client.post(
            "/api/v1/register?use_cookies=true", 
            json=user_data
        )
        
        assert response.status_code == 201
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_duplicate_email_registration(self, client: AsyncClient, db_session: AsyncSession):
        """Тест регистрации с дублирующимся email"""
        user_data = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "SecurePass123"
        }
        
        # Первая регистрация
        response1 = await client.post("/api/v1/register", json=user_data)
        assert response1.status_code == 201
        
        # Попытка повторной регистрации с тем же email
        user_data["username"] = "user2"
        response2 = await client.post("/api/v1/register", json=user_data)
        
        assert response2.status_code == 409
        data = response2.json()
        assert data["success"] is False
        assert "email" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_duplicate_username_registration(self, client: AsyncClient, db_session: AsyncSession):
        """Тест регистрации с дублирующимся username"""
        user_data = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "SecurePass123"
        }
        
        # Первая регистрация
        response1 = await client.post("/api/v1/register", json=user_data)
        assert response1.status_code == 201
        
        # Попытка повторной регистрации с тем же username
        user_data["email"] = "user2@example.com"
        response2 = await client.post("/api/v1/register", json=user_data)
        
        assert response2.status_code == 409
        data = response2.json()
        assert data["success"] is False
        assert "username" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_invalid_email_format(self, client: AsyncClient):
        """Тест регистрации с невалидным email"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "SecurePass123"
        }
        
        response = await client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_weak_password(self, client: AsyncClient):
        """Тест регистрации со слабым паролем"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"  # Слабый пароль
        }
        
        response = await client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client: AsyncClient):
        """Тест регистрации с отсутствующими обязательными полями"""
        user_data = {
            "username": "testuser",
            # Отсутствуют email и password
        }
        
        response = await client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
