from typing import Any, Optional

from starlette import status

from app.core.exceptions import BaseAPIException


class CardAlreadyExistsError(BaseAPIException):
    """
    Исключение, которое выбрасывается, когда карточка уже существует.
    Наследуется от BaseAPIException и используется для обработки ошибок
    при попытке создания карточки, которая уже есть в базе данных.

    Attributes:
        field (Optional[str]): Поле, по которому искали карточку.
        value (Any): Значение поля, по которому искали карточку.
        detail (Optional[str]): Подробное сообщение об ошибке.
    """

    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Карточка уже существует"
        if field and value is not None:
            message = f"Карточка с {field}={value} уже существует"

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            error_type="card_already_exists",
            extra={"field": field, "value": value} if field else None,
        )


class CardNotFoundError(BaseAPIException):
    """
    Исключение, которое выбрасывается, когда карточка не найдена.
    Наследуется от BaseAPIException и используется для обработки ошибок
    при работе с карточками товаров в приложении.

    Attributes:
        field (Optional[str]): Поле, по которому искали карточку.
        value (Any): Значение поля, по которому искали карточку.
        detail (Optional[str]): Подробное сообщение об ошибке.
    """

    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "карточка не найдена"
        if field and value is not None:
            message = f"карточка с {field}={value} не найдена"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
            error_type="card_not_found",
            extra={"field": field, "value": value} if field else None,
        )
