"""Утилиты для тестов."""
from typing import Dict, Any, List
from httpx import AsyncClient
from unittest.mock import patch
from app.models import UserRole
from app.schemas.v1.users.base import UserSchema
from decimal import Decimal
from datetime import datetime


def create_test_user_data() -> Dict[str, Any]:
    """Создает тестовые данные пользователя."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "phone": "+7 (999) 123-45-67"
    }


def assert_response_structure(response_data: Dict[str, Any], required_fields: List[str]):
    """Проверяет структуру ответа API."""
    for field in required_fields:
        assert field in response_data, f"Поле '{field}' отсутствует в ответе"


async def create_authenticated_client(client: AsyncClient, user_data: Dict[str, Any]) -> Dict[str, str]:
    """Создает заголовки для аутентифицированного клиента."""
    return {"Authorization": "Bearer fake_token"}


def create_mock_user_data(user_id: int = 1) -> UserSchema:
    """Создает данные мок-пользователя для тестов."""
    return UserSchema(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        phone=None,
        role=UserRole.USER,
        first_name=None,
        last_name=None,
        middle_name=None,
        birth_date=None,
        gender=None,
        avatar=None,
        is_active=True,
        is_verified=True,
        is_online=False,
        balance=Decimal("0.00"),
        bonus_points=0,
        cashback_balance=Decimal("0.00"),
        email_notifications=True,
        sms_notifications=False,
        push_notifications=True,
        marketing_consent=False,
        referral_code=None,
        referred_by_id=None,
        total_orders=0,
        total_spent=Decimal("0.00"),
        last_order_date=None,
        last_login=None,
        registration_source=None,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1)
    )
