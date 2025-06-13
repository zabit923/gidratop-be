from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.dependencies import get_db_session
from app.core.security.auth import get_current_user
from app.models import UserModel
from app.routes.base import BaseRouter
from app.schemas import (
    CartItemCreateSchema,
    CategoryResponseSchema,
    ProductResponseSchema,
)
from app.services.v1.carts.service import CartService


class CartRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="carts", tags=["Carts"])

    def configure(self):
        @self.router.post(
            path="/add-to-cart",
            response_model=ProductResponseSchema,
            status_code=status.HTTP_201_CREATED,
            summary="Добавление товара в корзину",
        )
        async def add_to_cart(
            data: CartItemCreateSchema,
            user: UserModel = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> CategoryResponseSchema:
            return await CartService(session).add_product_to_cart(user, data)
