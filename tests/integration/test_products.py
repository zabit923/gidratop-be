from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.schemas import ProductDataSchema
from tests.utils.helpers import create_mock_data


class TestProductRouter:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_product(self, auth_client: AsyncClient):
        response = await auth_client.post(
            "/api/v1/products",
            json={
                "title": "Test Product1",
                "description": "Test Description1",
                "price": 19.99,
                "quantity": 10,
            },
        )
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["title"] == "Test Product1"
        assert response_data["description"] == "Test Description1"
        assert response_data["price"] == 19.99
        assert response_data["quantity"] == 10

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_products_without_pagination(self, client: AsyncClient):
        with patch(
            "app.services.v1.products.service.ProductService.get_all_products"
        ) as mock_get_products:
            mock_products = [
                create_mock_data(ProductDataSchema, {"images": None}, id_value=1),
                create_mock_data(ProductDataSchema, {"images": None}, id_value=2),
                create_mock_data(ProductDataSchema, {"images": None}, id_value=3),
            ]
            mock_get_products.return_value = (mock_products, 3)

            response = await client.get("/api/v1/products")
            assert response.status_code == 200
            assert response.json()["data"]["total"] == 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_products_with_pagination(self, client: AsyncClient):
        with patch(
            "app.services.v1.products.service.ProductService.get_all_products"
        ) as mock_get_products:
            mock_products = [
                create_mock_data(ProductDataSchema, {"images": None}, id_value=i)
                for i in range(1, 11)
            ]
            mock_get_products.return_value = (mock_products, 10)

            response = await client.get("/api/v1/products?skip=0&limit=10")
            assert response.status_code == 200
            assert len(response.json()["data"]["items"]) == 10

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_product_by_id(self, client: AsyncClient):
        with patch(
            "app.services.v1.products.service.ProductService.get_product_by_id"
        ) as mock_get_product:
            mock_product = create_mock_data(
                ProductDataSchema, {"images": None}, id_value=1
            )
            mock_get_product.return_value = mock_product

            response = await client.get("/api/v1/products/1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_update_product(self, auth_client: AsyncClient):
        with patch(
            "app.services.v1.products.service.ProductService.update_product"
        ) as mock_updated_product:
            mock_product = create_mock_data(
                ProductDataSchema,
                {"title": "Updated Product", "images": None},
                id_value=1,
            )
            mock_updated_product.return_value = mock_product

            response = await auth_client.patch(
                "/api/v1/products/1",
                json={"title": "Updated Product"},
            )

            assert response.status_code == 200
            assert response.json()["title"] == "Updated Product"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_delete_product(self, auth_client: AsyncClient):
        with patch(
            "app.services.v1.products.service.ProductService.delete_product"
        ) as mock_delete_product:
            mock_delete_product.return_value = None
            response = await auth_client.delete("/api/v1/products/1")
            assert response.status_code == 204
