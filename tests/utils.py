"""
Утилиты для тестов.
"""
from typing import Dict, Any


def create_test_user_data() -> Dict[str, Any]:
    """Создает тестовые данные пользователя."""
    return {
        "username": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }


def assert_response_structure(response_data: Dict[str, Any], expected_keys: list):
    """Проверяет структуру ответа API."""
    for key in expected_keys:
        assert key in response_data, f"Ключ '{key}' отсутствует в ответе"


async def create_authenticated_client(client, user_data: Dict[str, Any]):
    """Создает аутентифицированного клиента."""
    # Регистрируем пользователя
    await client.post("/api/v1/register", json=user_data)
    
    # Логинимся
    login_response = await client.post("/api/v1/auth", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    
    token = login_response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
