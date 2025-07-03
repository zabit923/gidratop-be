from unittest.mock import patch
import pytest
from uuid import UUID
from httpx import AsyncClient

from app.schemas.v1.favorites import FavoriteBaseSchema
from tests.utils.helpers import create_mock_data


class TestFavoriteSchemas:
    """Тесты для схем избранных товаров."""

    def test_favorite_base_schema(self):
        """Тест базовой схемы избранного товара."""
        # Создаем тестовые данные
        user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        product_id = UUID("123e4567-e89b-12d3-a456-426614174001")

        # Создаем экземпляр схемы
        favorite_data = FavoriteBaseSchema(
            user_id=user_id,
            product_id=product_id
        )

        # Проверяем, что данные корректно валидируются
        assert favorite_data.user_id == user_id
        assert favorite_data.product_id == product_id
        assert isinstance(favorite_data.user_id, UUID)
        assert isinstance(favorite_data.product_id, UUID)


class TestFavoriteRouter:
    """Тесты для роутера избранных товаров."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_add_to_favorites(self, auth_client: AsyncClient):
        """Тест добавления товара в избранное."""
        with patch(
            "app.services.v1.favorites.service.FavoriteService.add_to_favorites"
        ) as mock_add_to_favorites:
            mock_add_to_favorites.return_value = create_mock_data(
                FavoriteBaseSchema,
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "product_id": "123e4567-e89b-12d3-a456-426614174001"
                }
            )

            response = await auth_client.post(
                "/api/v1/favorites",
                json={
                    "product_id": "123e4567-e89b-12d3-a456-426614174001"
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert data["product_id"] == "123e4567-e89b-12d3-a456-426614174001"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_favorites(self, auth_client: AsyncClient):
        """Тест получения списка избранных товаров."""
        with patch(
            "app.services.v1.favorites.service.FavoriteService.get_user_favorites"
        ) as mock_get_favorites:
            mock_favorites = [
                create_mock_data(
                    FavoriteBaseSchema,
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "product_id": f"123e4567-e89b-12d3-a456-42661417400{i}"
                    }
                )
                for i in range(1, 4)
            ]
            mock_get_favorites.return_value = (mock_favorites, 3)

            response = await auth_client.get("/api/v1/favorites")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["total"] == 3
            assert len(data["data"]["items"]) == 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_remove_from_favorites(self, auth_client: AsyncClient):
        """Тест удаления товара из избранного."""
        with patch(
            "app.services.v1.favorites.service.FavoriteService.remove_from_favorites"
        ) as mock_remove_from_favorites:
            mock_remove_from_favorites.return_value = None

            response = await auth_client.delete(
                "/api/v1/favorites/123e4567-e89b-12d3-a456-426614174001"
            )

            assert response.status_code == 204

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_check_favorite_status(self, auth_client: AsyncClient):
        """Тест проверки, находится ли товар в избранном."""
        with patch(
            "app.services.v1.favorites.service.FavoriteService.check_favorite_status"
        ) as mock_check_favorite:
            mock_check_favorite.return_value = True

            response = await auth_client.get(
                "/api/v1/favorites/check/123e4567-e89b-12d3-a456-426614174001"
            )

            assert response.status_code == 200
            assert response.json()["is_favorite"] is True
