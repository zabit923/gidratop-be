from typing import Optional

from starlette import status

from app.core.exceptions import BaseAPIException


class OutOfStockError(BaseAPIException):
    """
    Исключение, возникающее при попытке добавить товар в корзину,
    когда товар отсутствует на складе.
    """

    def __init__(
        self,
        product_id: Optional[int] = None,
        available_quantity: Optional[int] = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Не возможно добавить товар в корзину"
        if product_id and available_quantity is not None:
            message = (
                f"Товар с ID {product_id} отсутствует на складе,"
                f"либо его недостаточно для добавления в корзину."
                f"Доступное количество: {available_quantity}."
            )

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            error_type="quantity_out_of_stock",
        )
