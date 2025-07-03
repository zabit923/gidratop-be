from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.schemas import CardDataSchema, CategoryDataSchema
from tests.utils.helpers import assert_response_structure, create_mock_data


class TestCardsRouter:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_card(self, auth_client: AsyncClient):
        response = await auth_client.post(
            "/api/v1/cards",
            json={"title": "Test Card1"},
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
                "image",
            ],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_card_by_id(self, client: AsyncClient):
        with patch(
            "app.services.v1.cards.service.CardService.get_card_by_id"
        ) as mock_get_card:
            mock_card = create_mock_data(CardDataSchema, id_value=1)
            mock_get_card.return_value = mock_card

            response = await client.get("/api/v1/cards/1")
            assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_card(self, client: AsyncClient):
        with patch(
            "app.services.v1.cards.service.CardService.get_all_cards"
        ) as mock_get_cards:
            mock_cards = [
                create_mock_data(CardDataSchema, id_value=1),
                create_mock_data(CardDataSchema, id_value=2),
                create_mock_data(CardDataSchema, id_value=3),
            ]
            mock_get_cards.return_value = (mock_cards, 3)

            response = await client.get("/api/v1/cards")
            assert response.status_code == 200
            assert response.json()["data"]["total"] == 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_cards_with_pagination(self, client: AsyncClient):
        with patch(
            "app.services.v1.cards.service.CardService.get_all_cards"
        ) as mock_get_cards:
            mock_cards = [
                create_mock_data(CardDataSchema, id_value=i) for i in range(1, 11)
            ]
            mock_get_cards.return_value = (mock_cards, 10)

            response = await client.get("/api/v1/cards?skip=0&limit=10")
            assert response.status_code == 200
            assert len(response.json()["data"]["items"]) == 10

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_update_card(self, auth_client: AsyncClient):
        with patch(
            "app.services.v1.cards.service.CardService.update_card"
        ) as mock_updated_card:
            mock_card = create_mock_data(
                CategoryDataSchema, {"title": "Updated Card"}, id_value=1
            )
            mock_updated_card.return_value = mock_card

            response = await auth_client.patch(
                "/api/v1/cards/1",
                data={"title": "Updated Card"},
            )

            assert response.status_code == 200
            assert response.json()["title"] == "Updated Card"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_delete_card(self, auth_client: AsyncClient):
        with patch(
            "app.services.v1.cards.service.CardService.delete_card"
        ) as mock_delete_card:
            mock_delete_card.return_value = None
            response = await auth_client.delete("/api/v1/cards/1")
            assert response.status_code == 204
