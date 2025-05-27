"""
Модуль схем пользователя.

Содержит Pydantic схемы для работы с пользователями в API.
Включает схемы для различных представлений пользователя:
от базовой информации до детальных данных профиля.

Схемы:
    - UserSchema: Полная схема пользователя с основными полями
    - UserPublicSchema: Публичная схема пользователя (безопасная для показа)
    - UserPrivateSchema: Приватная схема с конфиденциальными данными
    - UserProfileSchema: Схема профиля с персональной информацией
    - CurrentUserSchema: Схема текущего аутентифицированного пользователя
    - UserDetailDataSchema: Детальная информация о пользователе
    - UserStatusDataSchema: Схема статуса пользователя (онлайн/оффлайн)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import EmailStr, Field

from app.models.v1.users import UserRole
from app.schemas.v1.base import BaseSchema, CommonBaseSchema


class UserSchema(BaseSchema):
    """
    Основная схема пользователя с базовыми полями.

    Содержит основную информацию о пользователе, включая аутентификационные
    данные, контактную информацию и статусы. Используется для большинства
    операций с пользователями в API.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        username (str): Имя пользователя для входа в систему
        email (EmailStr): Email адрес пользователя
        phone (str | None): Номер телефона пользователя
        role (UserRole): Роль пользователя в системе
        avatar (str | None): URL аватара пользователя
        is_active (bool): Статус активности аккаунта
        is_verified (bool): Статус верификации email/телефона
        created_at (datetime): Дата создания аккаунта
        updated_at (datetime): Дата последнего обновления

    Example:
        ```python
        user = UserSchema(
            id=123,
            username="john_doe",
            email="john@example.com",
            role=UserRole.USER,
            is_active=True,
            is_verified=False
        )
        ```
    """

    username: str = Field(
        description="Имя пользователя для входа в систему",
        examples=["john_doe", "user123"],
    )

    email: EmailStr = Field(
        description="Email адрес пользователя", examples=["user@example.com"]
    )

    phone: Optional[str] = Field(
        default=None,
        description="Номер телефона пользователя",
        examples=["+7 (999) 123-45-67", None],
    )

    role: UserRole = Field(
        default=UserRole.USER, description="Роль пользователя в системе"
    )

    avatar: Optional[str] = Field(
        default=None,
        description="URL аватара пользователя",
        examples=["https://example.com/avatar.jpg", None],
    )

    is_active: bool = Field(default=True, description="Статус активности аккаунта")

    is_verified: bool = Field(
        default=False, description="Статус верификации email/телефона"
    )


class UserPublicSchema(CommonBaseSchema):
    """
    Публичная схема пользователя для безопасного отображения.

    Содержит только те данные пользователя, которые безопасно показывать
    другим пользователям или в публичных API. Исключает конфиденциальную
    информацию такую как email, телефон и финансовые данные.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        username (str): Имя пользователя
        avatar (str | None): URL аватара пользователя
        role (UserRole): Роль пользователя (если не скрыта)
        is_active (bool): Статус активности (для модерации)

    Usage:
        Используется в списках пользователей, комментариях, отзывах
        и других местах где нужно показать базовую информацию о пользователе.
    """

    id: int = Field(description="Уникальный идентификатор пользователя")
    username: str = Field(description="Имя пользователя")
    avatar: Optional[str] = Field(default=None, description="URL аватара")
    role: UserRole = Field(description="Роль пользователя")
    is_active: bool = Field(description="Статус активности")


class UserPrivateSchema(BaseSchema):
    """
    Приватная схема пользователя с конфиденциальными данными.

    Содержит полную информацию о пользователе, включая финансовые данные,
    настройки уведомлений и статистику. Используется только для владельца
    аккаунта или администраторов.

    Attributes:
        Все поля из UserSchema плюс:
        first_name (str | None): Имя пользователя
        last_name (str | None): Фамилия пользователя
        middle_name (str | None): Отчество пользователя
        birth_date (date | None): Дата рождения
        gender (str | None): Пол пользователя
        balance (Decimal): Основной баланс
        bonus_points (int): Бонусные баллы
        cashback_balance (Decimal): Баланс кешбэка
        email_notifications (bool): Настройка email уведомлений
        sms_notifications (bool): Настройка SMS уведомлений
        push_notifications (bool): Настройка push уведомлений
        marketing_consent (bool): Согласие на маркетинг
        referral_code (str | None): Реферальный код
        total_orders (int): Общее количество заказов
        total_spent (Decimal): Общая потраченная сумма
        last_order_date (datetime | None): Дата последнего заказа
        last_login (datetime | None): Время последнего входа
        registration_source (str | None): Источник регистрации
    """

    # Наследуем все поля из UserSchema
    username: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole = UserRole.USER
    avatar: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False

    # Персональная информация
    first_name: Optional[str] = Field(
        default=None, description="Имя пользователя", examples=["Иван", "John"]
    )

    last_name: Optional[str] = Field(
        default=None, description="Фамилия пользователя", examples=["Иванов", "Doe"]
    )

    middle_name: Optional[str] = Field(
        default=None, description="Отчество пользователя", examples=["Иванович", None]
    )

    birth_date: Optional[date] = Field(
        default=None, description="Дата рождения пользователя", examples=["1990-01-15"]
    )

    gender: Optional[str] = Field(
        default=None,
        description="Пол пользователя",
        examples=["male", "female", "other"],
    )

    # Финансовые данные
    balance: Decimal = Field(
        default=Decimal("0.00"),
        description="Основной баланс пользователя в рублях",
        examples=[1500.50, 0.00],
    )

    bonus_points: int = Field(
        default=0, description="Количество бонусных баллов", examples=[250, 0]
    )

    cashback_balance: Decimal = Field(
        default=Decimal("0.00"),
        description="Баланс кешбэка в рублях",
        examples=[75.25, 0.00],
    )

    # Настройки уведомлений
    email_notifications: bool = Field(
        default=True, description="Получать уведомления на email"
    )

    sms_notifications: bool = Field(
        default=False, description="Получать SMS уведомления"
    )

    push_notifications: bool = Field(
        default=True, description="Получать push уведомления"
    )

    marketing_consent: bool = Field(
        default=False, description="Согласие на получение маркетинговых материалов"
    )

    # Реферальная система
    referral_code: Optional[str] = Field(
        default=None,
        description="Реферальный код пользователя",
        examples=["REF123ABC", None],
    )

    # Статистика
    total_orders: int = Field(
        default=0, description="Общее количество заказов пользователя", examples=[15, 0]
    )

    total_spent: Decimal = Field(
        default=Decimal("0.00"),
        description="Общая потраченная сумма в рублях",
        examples=[25000.00, 0.00],
    )

    last_order_date: Optional[datetime] = Field(
        default=None,
        description="Дата последнего заказа",
        examples=["2024-01-15T14:30:00Z"],
    )

    last_login: Optional[datetime] = Field(
        default=None,
        description="Время последнего входа в систему",
        examples=["2024-01-20T09:15:00Z"],
    )

    registration_source: Optional[str] = Field(
        default=None,
        description="Источник регистрации пользователя",
        examples=["web", "mobile", "api"],
    )


class UserProfileSchema(CommonBaseSchema):
    """
    Схема профиля пользователя для редактирования.

    Содержит поля профиля, которые пользователь может редактировать.
    Исключает системные поля и финансовые данные.

    Attributes:
        first_name (str | None): Имя
        last_name (str | None): Фамилия
        middle_name (str | None): Отчество
        birth_date (date | None): Дата рождения
        gender (str | None): Пол
        avatar (str | None): URL аватара
        phone (str | None): Номер телефона
        email_notifications (bool): Настройка email уведомлений
        sms_notifications (bool): Настройка SMS уведомлений
        push_notifications (bool): Настройка push уведомлений
        marketing_consent (bool): Согласие на маркетинг
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    marketing_consent: bool = False


class CurrentUserSchema(CommonBaseSchema):
    """
    Схема текущего аутентифицированного пользователя.

    Используется для передачи информации о текущем пользователе
    в контексте аутентификации. Содержит минимальный набор данных
    необходимых для авторизации и отображения в интерфейсе.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        username (str): Имя пользователя для входа
        email (EmailStr): Email адрес пользователя
        role (UserRole): Роль пользователя в системе
        is_active (bool): Статус активности аккаунта
        is_verified (bool): Статус верификации email/телефона

    Usage:
        ```python
        @router.get("/me", response_model=CurrentUserSchema)
        async def get_current_user(
            current_user: UserModel = Depends(get_current_user)
        ):
            return CurrentUserSchema.model_validate(current_user)
        ```
    """

    id: int = Field(description="Уникальный идентификатор пользователя")
    username: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Email адрес пользователя")
    role: UserRole = Field(description="Роль пользователя")
    is_active: bool = Field(default=True, description="Статус активности")
    is_verified: bool = Field(default=False, description="Статус верификации")


class UserDetailDataSchema(BaseSchema):
    """
    Схема детальной информации о пользователе для административных целей.

    Используется администраторами для просмотра подробной информации
    о пользователях. Содержит расширенный набор данных без финансовой
    информации.

    Attributes:
        username (str): Имя пользователя
        email (str): Email адрес пользователя
        role (UserRole): Роль пользователя в системе
        is_active (bool): Статус активности аккаунта
        is_verified (bool): Статус верификации
        registration_source (str | None): Источник регистрации
        last_login (datetime | None): Время последнего входа
        total_orders (int): Общее количество заказов

    Usage:
        Используется в административных панелях для управления пользователями.
    """

    username: str = Field(description="Имя пользователя")
    email: str = Field(description="Email адрес")
    role: UserRole = Field(description="Роль пользователя")
    is_active: bool = Field(default=True, description="Статус активности")
    is_verified: bool = Field(default=False, description="Статус верификации")
    registration_source: Optional[str] = Field(
        default=None, description="Источник регистрации"
    )
    last_login: Optional[datetime] = Field(
        default=None, description="Время последнего входа"
    )
    total_orders: int = Field(default=0, description="Общее количество заказов")


class UserStatusDataSchema(CommonBaseSchema):
    """
    Схема данных о статусе активности пользователя.

    Используется для отображения онлайн статуса пользователей
    в реальном времени. Может использоваться в чатах, списках
    пользователей и других интерактивных элементах.

    Attributes:
        is_online (bool): Находится ли пользователь онлайн
        last_activity (int | None): Время последней активности в Unix timestamp

    Example:
        ```python
        status = UserStatusDataSchema(
            is_online=True,
            last_activity=1642248600  # 2022-01-15 12:30:00 UTC
        )
        ```

    Usage:
        ```python
        @router.get("/users/{user_id}/status")
        async def get_user_status(user_id: int) -> UserStatusDataSchema:
            # Логика получения статуса
            return status
        ```
    """

    is_online: bool = Field(
        description="Находится ли пользователь онлайн в данный момент"
    )

    last_activity: Optional[int] = Field(
        default=None,
        description="Время последней активности в Unix timestamp (секунды)",
        examples=[1642248600, None],
    )
