from typing import Any, Optional

from starlette import status

from app.core.exceptions import BaseAPIException


class BrandNotFoundError(BaseAPIException):
    """
    Исключение, которое выбрасывается, когда бренд не найдена.
    Наследуется от BaseAPIException и используется для обработки ошибок
    при работе с брендами товаров в приложении.

    Attributes:
        field (Optional[str]): Поле, по которому искали бренд.
        value (Any): Значение поля, по которому искали бренд.
        detail (Optional[str]): Подробное сообщение об ошибке.
    """

    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Бренд не найдена"
        if field and value is not None:
            message = f"Бренд с {field}={value} не найдена"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
            error_type="brand_not_found",
            extra={"field": field, "value": value} if field else None,
        )


class BrandAlreadyExistsError(BaseAPIException):
    """
    Исключение, которое выбрасывается, когда бренд уже существует.
    Наследуется от BaseAPIException и используется для обработки ошибок
    при попытке создания бренда, которая уже есть в базе данных.

    Attributes:
        field (Optional[str]): Поле, по которому искали бренд.
        value (Any): Значение поля, по которому искали бренд.
        detail (Optional[str]): Подробное сообщение об ошибке.
    """

    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Бренд уже существует"
        if field and value is not None:
            message = f"Бренд с {field}={value} уже существует"

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            error_type="brand_already_exists",
            extra={"field": field, "value": value} if field else None,
        )
