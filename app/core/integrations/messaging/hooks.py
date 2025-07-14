"""
Модуль хуков для управления жизненным циклом системы сообщений.

Содержит обработчики событий FastStream для инициализации и настройки
системы очередей RabbitMQ при запуске и остановке приложения.

Хуки:
- setup_queues: Создание очередей после запуска приложения

Этот модуль обеспечивает:
- Автоматическое создание необходимых очередей
- Правильную инициализацию RabbitMQ при запуске
- Логирование процесса настройки
"""
import logging

from fastapi import FastAPI

from .broker import rabbit_router

logger = logging.getLogger("app.faststream.hooks")


@rabbit_router.after_startup
async def setup_queues(app: FastAPI) -> None:
    """
    Создает необходимые очереди в RabbitMQ после запуска приложения.

    Этот хук выполняется после успешного подключения к RabbitMQ
    и создает все необходимые очереди для работы системы email.

    Создаваемые очереди:
    - email_queue: Для обычных email сообщений
    - verification_email_queue: Для писем верификации
    - password_reset_email_queue: Для писем сброса пароля
    - registration_success_email_queue: Для писем об успешной регистрации

    Args:
        app (FastAPI): Экземпляр FastAPI приложения

    Returns:
        None

    Raises:
        Exception: Логируется, но не пробрасывается для предотвращения
                  сбоя запуска приложения

    Note:
        Все очереди создаются с настройками по умолчанию:
        - Durable: True (переживают перезапуск RabbitMQ)
        - Auto-delete: False (не удаляются автоматически)
        - Exclusive: False (доступны для множественных подключений)
    """
    logger.info("Настройка очередей RabbitMQ для отправки email")

    # Объявляем все необходимые очереди
    queues = [
        "email_queue",
        "verification_email_queue",
        "password_reset_email_queue",
        "registration_success_email_queue",
    ]

    # Создаем каждую очередь
    for queue_name in queues:
        try:
            # Объявляем очередь через broker
            # FastStream автоматически создаст очередь, если она не существует
            await rabbit_router.broker.declare_queue(queue_name)
            logger.info("Очередь %s успешно создана/проверена", queue_name)
        except Exception as e:
            # Логируем ошибку, но не прерываем запуск приложения
            logger.error("Ошибка при создании очереди %s: %s", queue_name, str(e))

    logger.info("Настройка очередей завершена")
