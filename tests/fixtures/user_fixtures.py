import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.v1.user import User
from app.core.security import get_password_hash


@pytest.fixture
async def test_user_data():
    """Базовые данные тестового пользователя"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123",
        "phone": "+7 (999) 123-45-67"
    }


@pytest.fixture
async def created_user(db_session: AsyncSession, test_user_data):
    """Создает пользователя в БД для тестов"""
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        phone=test_user_data.get("phone")
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user
