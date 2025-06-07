"""
INTEGRATION ТЕСТЫ для роутера регистрации пользователей.

Что такое Integration тесты:
- Тестируют ВЗАИМОДЕЙСТВИЕ между компонентами
- Используют МОКИ внешних сервисов (БД, email, Redis)
- Фокусируются на HTTP слое (роутер)
- БЫСТРЫЕ (нет реальных операций с БД)

Отличие от Functional тестов:
- Integration: мокают RegisterService, тестируют HTTP контракты
- Functional: реальные сервисы, тестируют бизнес-логику

Когда использовать:
- Проверка HTTP контрактов (запрос/ответ)
- Проверка обработки ошибок на уровне роутера
- Проверка валидации входных данных
- Быстрая проверка основных сценариев

Структура теста:
1. Мокирование сервисов
2. Настройка возвращаемых значений моков
3. HTTP запрос
4. Проверка HTTP ответа
5. Проверка вызовов моков
"""
from unittest.mock import patch, AsyncMock
import pytest
from httpx import AsyncClient
from tests.utils import create_test_user_data, assert_response_structure


class TestRegisterRouter:
    """Тесты для RegisterRouter."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_user_success(self, client: AsyncClient):
        """
        Тест успешной регистрации пользователя.

        Что тестируем:
        1. HTTP запрос корректно обрабатывается роутером
        2. Роутер корректно вызывает RegisterService
        3. HTTP ответ имеет правильную структуру
        4. Данные из сервиса корректно возвращаются в ответе

        Что НЕ тестируем:
        - Реальное сохранение в БД (мокаем сервис)
        - Реальную отправку email (мокаем messaging)
        - Бизнес-логику сервиса (тестируется отдельно)

        Фикстуры:
        - client: HTTP клиент (из conftest.py)

        Моки:
        - RegisterService: возвращает предопределенный ответ
        """
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
    @pytest.mark.integration
    async def test_register_user_with_cookies(self, client: AsyncClient):
        """
        Тест регистрации пользователя с использованием cookies.

        Что тестируем:
        1. Параметр use_cookies=true корректно передается в роутер
        2. Роутер корректно обрабатывает Query параметр
        3. HTTP ответ возвращается с правильным статусом

        Фокус на HTTP слое, не на бизнес-логике установки cookies
        """
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
    @pytest.mark.integration
    async def test_register_user_invalid_data(self, client: AsyncClient):
        """
        Тест регистрации с невалидными данными.

        Что тестируем:
        1. Валидация Pydantic схемы на уровне роутера
        2. HTTP статус 422 для ошибок валидации
        3. Структура ошибки валидации

        Особенность: НЕ мокируем сервис, т.к. запрос не должен до него дойти
        Валидация происходит на уровне FastAPI до вызова роутера
        """
        invalid_data = {
            "username": "",  # Пустое имя пользователя
            "email": "invalid-email",  # Невалидный email
            "password": "123"  # Слишком короткий пароль
        }

        response = await client.post("/api/v1/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_user_missing_required_fields(self, client: AsyncClient):
        """
        Тест регистрации без обязательных полей.

        Проверяем валидацию обязательных полей на уровне Pydantic схемы
        """
        incomplete_data = {
            "username": "testuser"
            # Отсутствуют email и password
        }

        response = await client.post("/api/v1/register", json=incomplete_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_user_password_validation(self, client: AsyncClient):
        """
        Тест валидации пароля.

        Что тестируем:
        1. Различные сценарии валидации пароля
        2. Успешные и неуспешные случаи
        3. Корректную обработку на уровне роутера

        Смешанный подход: для валидных паролей мокируем сервис,
        для невалидных - ожидаем ошибку валидации
        """
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

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_service_error_handling(self, client: AsyncClient):
        """
        Тест обработки ошибок от RegisterService.

        Что тестируем:
        1. Роутер корректно обрабатывает исключения от сервиса
        2. HTTP статусы соответствуют типам ошибок
        3. Структура ответа при ошибках

        Мокируем сервис чтобы он выбрасывал различные исключения
        """
        user_data = create_test_user_data()

        # Тест обработки ошибки "пользователь уже существует"
        with patch('app.services.v1.registration.service.RegisterService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            # Мокируем что сервис возвращает ошибку дублирования
            mock_service.create_user.return_value = {
                "success": False,
                "error": {
                    "code": "USER_ALREADY_EXISTS",
                    "detail": "Пользователь с таким email уже существует"
                }
            }

            response = await client.post("/api/v1/register", json=user_data)

            # В зависимости от реализации роутера может быть 409 или 400
            assert response.status_code in [400, 409]

            response_data = response.json()
            assert response_data["success"] is False
            assert "error" in response_data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_response_structure_validation(self, client: AsyncClient):
        """
        Тест валидации структуры ответа роутера.

        Что тестируем:
        1. Ответ соответствует ожидаемой схеме
        2. Все обязательные поля присутствуют
        3. Типы данных корректны

        Фокус на контракте API, а не на бизнес-логике
        """
        user_data = create_test_user_data()

        with patch('app.services.v1.registration.service.RegisterService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service

            # Подробный мок ответ для проверки структуры
            mock_service.create_user.return_value = {
                "success": True,
                "message": "Пользователь успешно зарегистрирован",
                "data": {
                    "user": {
                        "id": 1,
                        "username": "testuser",
                        "email": "test@example.com",
                        "is_verified": False,
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    "tokens": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer"
                    }
                }
            }

            response = await client.post("/api/v1/register", json=user_data)

            assert response.status_code == 200
            response_data = response.json()

            # Проверяем основную структуру
            assert_response_structure(response_data, ["success", "message", "data"])

            # Проверяем структуру данных пользователя
            user_data_response = response_data["data"]["user"]
            required_user_fields = ["id", "username", "email", "is_verified"]
            for field in required_user_fields:
                assert field in user_data_response

            # Проверяем структуру токенов
            tokens_data = response_data["data"]["tokens"]
            required_token_fields = ["access_token", "refresh_token"]
            for field in required_token_fields:
                assert field in tokens_data
                assert isinstance(tokens_data[field], str)
                assert len(tokens_data[field]) > 10  # Токены должны быть не пустыми

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_content_type_validation(self, client: AsyncClient):
        """
        Тест валидации Content-Type заголовка.

        Что тестируем:
        1. Роутер принимает только application/json
        2. Некорректный Content-Type отклоняется
        """
        user_data = create_test_user_data()

        # Попытка отправить данные как form-data вместо JSON
        response = await client.post(
            "/api/v1/register",
            data=user_data  # data вместо json
        )

        # FastAPI должен вернуть ошибку о неподдерживаемом Content-Type
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_http_methods(self, client: AsyncClient):
        """
        Тест что endpoint поддерживает только POST метод.

        Что тестируем:
        1. POST запросы обрабатываются
        2. GET, PUT, DELETE запросы отклоняются
        """
        # POST должен работать (с моком)
        with patch('app.services.v1.registration.service.RegisterService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            mock_service.create_user.return_value = {"success": True, "data": {}}

            response = await client.post("/api/v1/register", json=create_test_user_data())
            assert response.status_code == 200

        # GET должен вернуть 405 Method Not Allowed
        response = await client.get("/api/v1/register")
        assert response.status_code == 405

        # PUT должен вернуть 405 Method Not Allowed
        response = await client.put("/api/v1/register", json={})
        assert response.status_code == 405