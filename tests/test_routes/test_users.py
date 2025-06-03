"""Тесты для роутера пользователей."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.models import UserRole
from tests.utils import create_test_user_data, assert_response_structure, create_authenticated_client


class TestUserRouter:
    """Тесты для UserRouter."""

    @pytest.mark.asyncio
    async def test_get_users_success(self, client: AsyncClient):
        """Тест успешного получения списка пользователей."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_users = [
                {
                    "id": 1,
                    "username": "user1",
                    "email": "user1@example.com",
                    "role": UserRole.USER,
                    "is_verified": True
                },
                {
                    "id": 2,
                    "username": "user2",
                    "email": "user2@example.com",
                    "role": UserRole.USER,
                    "is_verified": False
                }
            ]
            mock_get_users.return_value = (mock_users, 2)
            
            response = await client.get("/api/v1/users", headers=headers)
            
            assert response.status_code == 200
            response_data = response.json()
            
            assert_response_structure(response_data, ["data"])
            assert "items" in response_data["data"]
            assert "total" in response_data["data"]
            assert "page" in response_data["data"]
            assert "size" in response_data["data"]
            assert len(response_data["data"]["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_users_with_pagination(self, client: AsyncClient):
        """Тест получения пользователей с пагинацией."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            response = await client.get(
                "/api/v1/users?skip=10&limit=5", 
                headers=headers
            )
            
            assert response.status_code == 200
            mock_get_users.assert_called_once()
            
            # Проверяем, что пагинация передана правильно
            call_args = mock_get_users.call_args
            pagination = call_args.kwargs['pagination']
            assert pagination.skip == 10
            assert pagination.limit == 5

    @pytest.mark.asyncio
    async def test_get_users_with_sorting(self, client: AsyncClient):
        """Тест получения пользователей с сортировкой."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            response = await client.get(
                "/api/v1/users?sort_by=username&sort_desc=false", 
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            pagination = call_args.kwargs['pagination']
            assert pagination.sort_by == "username"
            assert pagination.sort_desc is False

    @pytest.mark.asyncio
    async def test_get_users_with_role_filter(self, client: AsyncClient):
        """Тест получения пользователей с фильтрацией по роли."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            response = await client.get(
                "/api/v1/users?role=admin", 
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            assert call_args.kwargs['role'] == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_get_users_with_search(self, client: AsyncClient):
        """Тест получения пользователей с поиском."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            search_term = "test_search"
            response = await client.get(
                f"/api/v1/users?search={search_term}", 
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            assert call_args.kwargs['search'] == search_term

    @pytest.mark.asyncio
    async def test_get_users_unauthorized(self, client: AsyncClient):
        """Тест получения пользователей без авторизации."""
        response = await client.get("/api/v1/users")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_users_forbidden(self, client: AsyncClient):
        """Тест получения пользователей с недостаточными правами."""
        user_data = create_test_user_data()
        
        with patch('app.core.security.auth.get_current_user') as mock_get_user:
            from fastapi import HTTPException
            mock_get_user.side_effect = HTTPException(
                status_code=403,
                detail="Недостаточно прав для выполнения операции"
            )
            
            response = await client.get(
                "/api/v1/users",
                headers={"Authorization": "Bearer invalid_token"}
            )
            
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_users_with_all_parameters(self, client: AsyncClient):
        """Тест получения пользователей со всеми параметрами одновременно."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            response = await client.get(
                "/api/v1/users?skip=5&limit=20&sort_by=email&sort_desc=true&role=user&search=john",
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            pagination = call_args.kwargs['pagination']
            assert pagination.skip == 5
            assert pagination.limit == 20
            assert pagination.sort_by == "email"
            assert pagination.sort_desc is True
            assert call_args.kwargs['role'] == UserRole.USER
            assert call_args.kwargs['search'] == "john"

    @pytest.mark.asyncio
    async def test_get_users_invalid_limit_too_high(self, client: AsyncClient):
        """Тест с превышением максимального лимита."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        response = await client.get(
            "/api/v1/users?limit=150",
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_users_invalid_limit_zero(self, client: AsyncClient):
        """Тест с нулевым лимитом."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        response = await client.get(
            "/api/v1/users?limit=0",
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_users_invalid_skip_negative(self, client: AsyncClient):
        """Тест с отрицательным значением skip."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        response = await client.get(
            "/api/v1/users?skip=-1",
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_users_invalid_sort_field(self, client: AsyncClient):
        """Тест с недопустимым полем сортировки."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        response = await client.get(
            "/api/v1/users?sort_by=invalid_field",
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_users_invalid_role(self, client: AsyncClient):
        """Тест с недопустимой ролью."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        response = await client.get(
            "/api/v1/users?role=invalid_role",
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_users_empty_search(self, client: AsyncClient):
        """Тест с пустой строкой поиска."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            response = await client.get(
                "/api/v1/users?search=",
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            assert call_args.kwargs['search'] == ""

    @pytest.mark.asyncio
    async def test_get_users_service_exception(self, client: AsyncClient):
        """Тест обработки исключения в сервисе."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.side_effect = Exception("Database error")
            
            response = await client.get("/api/v1/users", headers=headers)
            
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_get_users_large_dataset(self, client: AsyncClient):
        """Тест с большим количеством пользователей."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            # Создаем большой список пользователей
            mock_users = [
                {
                    "id": i,
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                    "role": UserRole.USER,
                    "is_verified": i % 2 == 0
                }
                for i in range(1, 101)
            ]
            mock_get_users.return_value = (mock_users, 1000)
            
            response = await client.get(
                "/api/v1/users?limit=100",
                headers=headers
            )
            
            assert response.status_code == 200
            response_data = response.json()
            assert len(response_data["data"]["items"]) == 100
            assert response_data["data"]["total"] == 1000

    @pytest.mark.asyncio
    async def test_get_users_special_characters_in_search(self, client: AsyncClient):
        """Тест поиска со специальными символами."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            special_search = "user@domain.com"
            response = await client.get(
                f"/api/v1/users?search={special_search}",
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            assert call_args.kwargs['search'] == special_search

    @pytest.mark.asyncio
    async def test_get_users_unicode_search(self, client: AsyncClient):
        """Тест поиска с Unicode символами."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            unicode_search = "пользователь"
            response = await client.get(
                f"/api/v1/users?search={unicode_search}",
                headers=headers
            )
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            assert call_args.kwargs['search'] == unicode_search

    @pytest.mark.asyncio
    async def test_get_users_default_values(self, client: AsyncClient):
        """Тест использования значений по умолчанию."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 0)
            
            response = await client.get("/api/v1/users", headers=headers)
            
            assert response.status_code == 200
            
            call_args = mock_get_users.call_args
            pagination = call_args.kwargs['pagination']
            assert pagination.skip == 0
            assert pagination.limit == 10
            assert pagination.sort_desc is True
            assert call_args.kwargs['role'] is None
            assert call_args.kwargs['search'] is None

    @pytest.mark.asyncio
    async def test_get_users_response_schema_validation(self, client: AsyncClient):
        """Тест валидации схемы ответа."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_users = [
                {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "role": UserRole.USER,
                    "is_verified": True,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z"
                }
            ]
            mock_get_users.return_value = (mock_users, 1)
            
            response = await client.get("/api/v1/users", headers=headers)
            
            assert response.status_code == 200
            response_data = response.json()
            
            # Проверяем структуру ответа
            assert "data" in response_data
            data = response_data["data"]
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "size" in data
            
            # Проверяем структуру элементов
            assert len(data["items"]) == 1
            user = data["items"][0]
            required_fields = ["id", "username", "email", "role", "is_verified"]
            for field in required_fields:
                assert field in user

    @pytest.mark.asyncio
    async def test_get_users_pagination_calculation(self, client: AsyncClient):
        """Тест правильности расчета пагинации."""
        user_data = create_test_user_data()
        headers = await create_authenticated_client(client, user_data)
        
        with patch('app.services.v1.users.service.UserService.get_users') as mock_get_users:
            mock_get_users.return_value = ([], 25)
            
            response = await client.get(
                "/api/v1/users?skip=10&limit=5",
                headers=headers
            )
            
            assert response.status_code == 200
            response_data = response.json()
            
            data = response_data["data"]
            assert data["total"] == 25
            assert data["page"] == 3