"""Тесты для роутера регистрации пользователей."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from tests.utils import create_test_user_data, assert_response_structure


class TestRegisterRouter:
    """Тесты для RegisterRouter."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient):
        """Тест успешной регистрации пользователя."""
        user_data = create_test_user_data()

        # Мокаем весь сервис регистрации
        with patch('app.services.v1.registration.service.RegisterService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            mock_service.create_user.return_value = {
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

    @pytest.mark.asyncio
    async def test_register_user_with_cookies(self, client: AsyncClient):
        """Тест регистрации пользователя с использованием cookies."""
        user_data = create_test_user_data()

        with patch('app.services.v1.registration.service.RegisterService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            mock_service.create_user.return_value = {
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
    async def test_register_user_password_validation(self, client: AsyncClient):
        """Тест валидации пароля."""
        test_cases = [
            {"password": "12345", "should_fail": True},  # Слишком короткий
            {"password": "onlyletters", "should_fail": True},  # Только буквы
            {"password": "12345678", "should_fail": True},  # Только цифры
            {"password": "ValidPass123!", "should_fail": False},  # Валидный пароль
        ]

        for case in test_cases:
            user_data = create_test_user_data()
            user_data["password"] = case["password"]

            if not case["should_fail"]:
                with patch('app.services.v1.registration.service.RegisterService') as mock_service_class:
                    mock_service = AsyncMock()
                    mock_service_class.return_value = mock_service

                    mock_service.create_user.return_value = {
                        "success": True,
                        "message": "Пользователь успешно зарегистрирован",
                        "data": {"user": {}, "tokens": {}}
                    }

                    response = await client.post("/api/v1/register", json=user_data)
                    assert response.status_code == 200
            else:
                response = await client.post("/api/v1/register", json=user_data)
                assert response.status_code in [401, 422]  # Может быть и 401 и 422
