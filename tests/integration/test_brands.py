from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.schemas import BrandDataSchema
from tests.utils.helpers import assert_response_structure, create_mock_data


class TestBrandsRouter:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_brand(self, auth_client: AsyncClient):
        response = await auth_client.post(
            "/api/v1/brands",
            json={"title": "Test Brand1"},
        )
        assert response.status_code == 201
        response_data = response.json()
        assert_response_structure(
            response_data,
            [
                "id",
                "created_at",
                "updated_at",
                "title",
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_brands(self, client: AsyncClient):
        with patch(
            "app.services.v1.brands.service.BrandService.get_all_brands"
        ) as mock_get_brands:
            mock_brands = [
                create_mock_data(BrandDataSchema, id_value=1),
                create_mock_data(BrandDataSchema, id_value=2),
                create_mock_data(BrandDataSchema, id_value=3),
            ]
            mock_get_brands.return_value = (mock_brands, 3)

            response = await client.get("/api/v1/brands")
            assert response.status_code == 200
            assert response.json()["data"]["total"] == 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_brands_with_pagination(self, client: AsyncClient):
        with patch(
            "app.services.v1.brands.service.BrandService.get_all_brands"
        ) as mock_get_brands:
            mock_brands = [
                create_mock_data(BrandDataSchema, id_value=i) for i in range(1, 11)
            ]
            mock_get_brands.return_value = (mock_brands, 10)

            response = await client.get("/api/v1/brands?skip=0&limit=10")
            assert response.status_code == 200
            assert len(response.json()["data"]["items"]) == 10

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_update_brand(self, auth_client: AsyncClient):
        with patch(
            "app.services.v1.brands.service.BrandService.update_brand"
        ) as mock_updated_brand:
            mock_brand = create_mock_data(
                BrandDataSchema, {"title": "Updated Brand"}, id_value=1
            )
            mock_updated_brand.return_value = mock_brand

            response = await auth_client.patch(
                "/api/v1/brands/1",
                data={"title": "Updated Brand"},
            )

            assert response.status_code == 200
            assert response.json()["title"] == "Updated Brand"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_delete_brand(self, auth_client: AsyncClient):
        with patch(
            "app.services.v1.brands.service.BrandService.delete_brand"
        ) as mock_delete_brand:
            mock_delete_brand.return_value = None
            response = await auth_client.delete("/api/v1/brands/1")
            assert response.status_code == 204
