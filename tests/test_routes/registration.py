"""Тесты для роутера регистрации пользователей."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.schemas import RegistrationRequestSchema
from tests.utils import create_test_user_data, assert_response_structure


class TestRegisterRouter:
    """Тесты для RegisterRouter."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient):
        """Тест успешной регистрации пользователя."""
        user_data = create_test_user_data()
        
        with patch('app.services.v1.registration.service.RegisterService.create_user') as mock_create:
            mock_create.return_value = {
                "success": True,
                "message": "Пользователь успешно зарегистрирован",
                "data": {
                    "user": {
                        "id": 1,
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "is_verified": False
                    },
                    "tokens": {
                        "access_token": "test_access_token",
                        "refresh_token": "test_refresh_token"
                    }
                }
            }
            
            response = await client.post("/api/v1/register", json=user_data)
            
            assert response.status_code == 200
            response_data = response.json()
            
            assert_response_structure(response_data, ["success", "message", "data"])
            assert response_data["success"] is True
            assert "зарегистрирован" in response_data["message"]
            assert "user" in response_data["data"]
            assert "tokens" in response_data["data"]

    @pytest.mark.asyncio
    async def test_register_user_with_cookies(self, client: AsyncClient):
        """Тест регистрации пользователя с использованием cookies."""
        user_data = create_test_user_data()
        
        with patch('app.services.v1.registration.service.RegisterService.create_user') as mock_create:
            mock_create.return_value = {
                "success": True,
                "message": "Пользователь успешно зарегистрирован",
                "data": {
                    "user": {
                        "id": 1,
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "is_verified": False
                    },
                    "tokens": {
                        "access_token": "test_access_token",
                        "refresh_token": "test_refresh_token"
                    }
                }
            }
            
            response = await client.post(
                "/api/v1/register?use_cookies=true", 
                json=user_data
            )
            
            assert response.status_code == 200
            # Проверяем, что куки установлены
            assert "Set-Cookie" in response.headers or len(response.cookies) > 0

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, client: AsyncClient):
        """Тест регистрации уже существующего пользователя."""
        user_data = create_test_user_data()
        
        with patch('app.services.v1.registration.service.RegisterService.create_user') as mock_create:
            from fastapi import HTTPException
            mock_create.side_effect = HTTPException(
                status_code=409,
                detail="Пользователь с таким email уже существует"
            )
            
            response = await client.post("/api/v1/register", json=user_data)
            
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_user_invalid_data(self, client: AsyncClient):
        """Тест регистрации с невалидными данными."""
        invalid_data = {
            "username": "",  # Пустое имя пользователя
            "email": "invalid-email",  # Невалидный email
            "password": "123"  # Слишком короткий пароль
        }
        
        response = await client.post("/api/v1/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_missing_required_fields(self, client: AsyncClient):
        """Тест регистрации без обязательных полей."""
        incomplete_data = {
            "username": "testuser"
            # Отсутствуют email и password
        }
        
        response = await client.post("/api/v1/register", json=incomplete_data)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_user_with_phone(self, client: AsyncClient):
        """Тест регистрации пользователя с номером телефона."""
        user_data = create_test_user_data()
        user_data["phone"] = "+7 (999) 123-45-67"
        
        with patch('app.services.v1.registration.service.RegisterService.create_user') as mock_create:
            mock_create.return_value = {
                "success": True,
                "message": "Пользователь успешно зарегистрирован",
                "data": {
                    "user": {
                        "id": 1,
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "phone": user_data["phone"],
                        "is_verified": False
                    },
                    "tokens": {
                        "access_token": "test_access_token",
                        "refresh_token": "test_refresh_token"
                    }
                }
            }
            
            response = await client.post("/api/v1/register", json=user_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["data"]["user"]["phone"] == user_data["phone"]

    @pytest.mark.asyncio
    async def test_register_user_service_error(self, client: AsyncClient):
        """Тест обработки ошибки сервиса регистрации."""
        user_data = create_test_user_data()
        
        with patch('app.services.v1.registration.service.RegisterService.create_user') as mock_create:
            from fastapi import HTTPException
            mock_create.side_effect = HTTPException(
                status_code=500,
                detail="Ошибка при создании пользователя"
            )
            
            response = await client.post("/api/v1/register", json=user_data)
            
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_register_user_password_validation(self, client: AsyncClient):
        """Тест валидации пароля."""
        test_cases = [
            {"password": "12345", "should_fail": True},  # Слишком короткий
            {"password": "onlyletters", "should_fail": True},  # Только буквы
            {"password": "12345678", "should_fail": True},  # Только цифры
            {"password": "ValidPass123", "should_fail": False},  # Валидный пароль
        ]
        
        for case in test_cases:
            user_data = create_test_user_data()
            user_data["password"] = case["password"]
            
            if not case["should_fail"]:
                with patch('app.services.v1.registration.service.RegisterService.create_user') as mock_create:
                    mock_create.return_value = {
                        "success": True,
                        "message": "Пользователь успешно зарегистрирован",
                        "data": {"user": {}, "tokens": {}}
                    }
                    
                    response = await client.post("/api/v1/register", json=user_data)
                    assert response.status_code == 200
            else:
                response = await client.post("/api/v1/register", json=user_data)
                assert response.status_code == 422

