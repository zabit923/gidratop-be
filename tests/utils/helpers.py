"""Утилиты для тестов."""
from decimal import Decimal
from datetime import datetime
import uuid
import random
import string
from typing import Dict, Any, List
from httpx import AsyncClient
from app.models import UserRole
from app.schemas.v1.users.base import UserSchema



def create_test_user_data() -> Dict[str, Any]:
    """Создает тестовые данные пользователя."""
    unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "SecurePass123!",
        "phone": f"+7 (999) {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
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
    # Генерируем UUID на основе user_id для предсказуемости в тестах
    user_uuid = uuid.UUID(int=user_id, version=None)

    return UserSchema(
        id=user_uuid,  # Используем UUID вместо int
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


def generate_test_uuid(seed: int = None) -> uuid.UUID:
    """
    Генерирует тестовый UUID.

    Args:
        seed: Число для генерации предсказуемого UUID (для тестов)

    Returns:
        UUID объект
    """
    if seed is not None:
        # Создаем предсказуемый UUID на основе seed
        return uuid.UUID(int=seed, version=None)
    else:
        # Генерируем случайный UUID
        return uuid.uuid4()


def create_mock_user_dict(user_id: int = 1) -> Dict[str, Any]:
    """
    Создает словарь с данными пользователя для мокирования.

    Используется когда нужен dict, а не Pydantic модель.
    """
    user_uuid = generate_test_uuid(user_id)

    return {
        "id": str(user_uuid),  # UUID как строка
        "username": f"user{user_id}",
        "email": f"user{user_id}@example.com",
        "phone": None,
        "role": UserRole.USER.value,
        "first_name": None,
        "last_name": None,
        "middle_name": None,
        "birth_date": None,
        "gender": None,
        "avatar": None,
        "is_active": True,
        "is_verified": True,
        "is_online": False,
        "balance": "0.00",
        "bonus_points": 0,
        "cashback_balance": "0.00",
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "marketing_consent": False,
        "referral_code": None,
        "referred_by_id": None,
        "total_orders": 0,
        "total_spent": "0.00",
        "last_order_date": None,
        "last_login": None,
        "registration_source": None,
        "created_at": datetime(2023, 1, 1).isoformat(),
        "updated_at": datetime(2023, 1, 1).isoformat()
    }


def create_test_user_with_uuid(**overrides) -> Dict[str, Any]:
    """
    Создает тестовые данные пользователя с UUID.

    Используется когда нужно создать пользователя с конкретным UUID.
    """
    user_data = create_test_user_data()

    if 'id' not in overrides:
        overrides['id'] = str(uuid.uuid4())

    user_data.update(overrides)
    return user_data
