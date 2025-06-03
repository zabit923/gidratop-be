"""Тесты для роутера пользователей."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
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