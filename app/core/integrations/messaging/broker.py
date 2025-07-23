"""
Модуль инициализации брокера сообщений RabbitMQ через FastStream.

Этот модуль создает основное соединение с RabbitMQ и предоставляет
router для интеграции с FastAPI приложением.

Компоненты:
- rabbit_router: Основной router FastStream для RabbitMQ
- broker: Экземпляр брокера для публикации сообщений

Использование:
    from .broker import rabbit_router, broker

    # Подключение к FastAPI
    app.include_router(rabbit_router)

    # Публикация сообщений
    await broker.publish(message, "queue_name")
"""

from faststream.rabbit.fastapi import RabbitRouter

from app.core.settings import settings

# Создаем router для RabbitMQ с автоматическим переподключением
rabbit_router = RabbitRouter(
    settings.rabbitmq_url,
    reconnect_interval=5.0,  # Интервал переподключения в секундах
)

# Экземпляр брокера для публикации сообщений
broker = rabbit_router.broker
